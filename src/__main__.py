import asyncio
import logging
import sys
import io
from .main import main

# 強制將標準輸出/錯誤輸出設定為 utf-8 編碼 (解決 Windows 終端機亂碼問題)
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

# Setup basic logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    asyncio.run(main())
