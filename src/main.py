"""
Scrape 104 HR Bank job postings using Apify SDK and BeautifulSoup.
"""

from apify import Actor
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio

async def main() -> None:
    async with Actor:
        # Get input configuration (configured via Apify interface or INPUT_SCHEMA.json)
        actor_input = await Actor.get_input() or {}
        keyword = actor_input.get('keyword', 'UIUX')
        area = actor_input.get('area', '6001001000,6001002000')
        max_jobs = actor_input.get('max_jobs', 30)
        
        # Format the search URL
        url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}&page=1"
        if area:
            url += f"&area={area}"
        
        Actor.log.info(f"開始抓取 104 職缺，關鍵字: {keyword}，目標筆數至少: {max_jobs}")
        Actor.log.info(f"目標網址: {url}")
        
        # 使用 Playwright 開啟無頭瀏覽器來執行 JavaScript
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            try:
                Actor.log.info("正在載入頁面並等待 JavaScript 渲染...")
                await page.goto(url, wait_until="networkidle")
                # 等待職缺列表的主要容器出現 (最多等 15 秒)
                await page.wait_for_selector('.job-list-container', timeout=15000)
                
                # 自動往下捲動迴圈
                previous_count = 0
                while True:
                    # 取得畫面上目前的職缺數量
                    current_count = await page.locator('.job-list-container').count()
                    Actor.log.info(f"目前畫面上已載入 {current_count} 筆職缺...")
                    
                    if current_count >= max_jobs:
                        Actor.log.info(f"已達目標筆數 ({max_jobs})，停止往下捲動。")
                        break
                        
                    # 嘗試捲動到底部
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2500)  # 等待新資料載入
                    
                    # 104 電腦版經常在捲動幾次後會出現「顯示更多」或需要點擊下一頁
                    # 我們可以試著檢查並點擊下一頁按鈕，或者單純依賴自動載入
                    next_page_btn = page.locator('button.js-next-page, a.page-next')
                    if await next_page_btn.count() > 0 and await next_page_btn.first.is_visible():
                        await next_page_btn.first.click()
                        await page.wait_for_timeout(2000)
                    
                    new_count = await page.locator('.job-list-container').count()
                    if new_count == previous_count:
                        Actor.log.info("往下捲動後沒有載入更多資料，可能已達搜尋結果最底端。")
                        break
                        
                    previous_count = new_count
                
            except Exception as e:
                Actor.log.warning(f"網頁載入可能逾時或發生錯誤: {e}")
            
            # 取得渲染後的 HTML
            html_content = await page.content()
            await browser.close()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the job containers
            jobs = soup.select('.job-list-container')
            # 限制處理筆數
            jobs = jobs[:max_jobs]
            
            Actor.log.info(f"準備開始解析 {len(jobs)} 個職缺資料...")
            Actor.log.info(f"本頁共找到 {len(jobs)} 個職缺")
            
            scraped_data = []
            
            for index, job in enumerate(jobs):
                try:
                    # 1. Job Basic Info
                    job_title_elem = job.select_one('.info-job__text')
                    title = job_title_elem.text.strip() if job_title_elem else None
                    job_url = job_title_elem['href'] if job_title_elem and 'href' in job_title_elem.attrs else None
                    if job_url is None and title is None:
                        continue # Skip empty containers
                    
                    desc_elem = job.select_one('.info-description')
                    description = desc_elem.text.strip() if desc_elem else None
                    
                    # 2. Company Basic Info
                    company_elem = job.select_one('.info-company__text')
                    company_name = company_elem.text.strip() if company_elem else None
                    company_url = company_elem['href'] if company_elem and 'href' in company_elem.attrs else None
                    
                    industry_elem = job.select_one('.info-company-addon-type')
                    industry_type = industry_elem.text.strip() if industry_elem else None
                    
                    # 3. tags (Location, Experience, Education, Salary)
                    tags = job.select('.info-tags.gray-deep-dark .info-tags__text')
                    location = tags[0].text.strip() if len(tags) > 0 else None
                    experience = tags[1].text.strip() if len(tags) > 1 else None
                    education = tags[2].text.strip() if len(tags) > 2 else None
                    salary = tags[3].text.strip() if len(tags) > 3 else None
                    
                    # 4. Benefits/Perks
                    benefits_elems = job.select('.info-othertags .info-othertags__text')
                    benefits = [b.text.strip() for b in benefits_elems] if benefits_elems else []
                    
                    # 5. Application Count
                    apply_range_elem = job.select_one('.action-apply__range')
                    apply_range = apply_range_elem.text.strip() if apply_range_elem else None
                    
                    job_info = {
                        "職務名稱": title,
                        "職務連結": job_url,
                        "公司名稱": company_name,
                        "公司連結": company_url,
                        "產業類別": industry_type,
                        "工作地點": location,
                        "經歷要求": experience,
                        "學歷要求": education,
                        "薪資待遇": salary,
                        "職務內容摘要": description,
                        "公司福利": benefits,
                        "應徵人數": apply_range
                    }
                    scraped_data.append(job_info)
                except Exception as e:
                    Actor.log.warning(f"Error parsing job {index}: {e}")
                
            # Save results back to Apify dataset
            await Actor.push_data(scraped_data)
            Actor.log.info(f"成功將 {len(scraped_data)} 筆符合條件的職缺儲存至 Apify Dataset！")

