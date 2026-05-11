# 使用官方 Python slim image
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 pipeline 預先安裝好的套件（不在 docker build 裡跑 pip install）
COPY vendor/ /usr/local/lib/python3.10/site-packages/

# 複製應用程式程式碼
COPY app/ ./app/
COPY static/ ./static/

# 不複製 qr_code.db（SQLite 會在啟動時自動建立）

# 暴露 port
EXPOSE 8000

# 啟動指令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
