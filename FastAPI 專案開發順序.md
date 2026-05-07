1. 環境設置
   └── 建立虛擬環境 (venv)
   └── 安裝套件 (requirements.txt)
   └── 建立資料夾結構

2. database.py
   └── 設定 DB 連線 (engine)
   └── 建立 Base、SessionLocal
   └── get_db() dependency

* database → models（有 DB 連線才能定義 schema）

3. models.py
   └── 定義資料表 (繼承 Base)

*models → schemas（知道資料表結構才能定義 API 格式）

4. schemas.py
   └── 定義 API 輸入/輸出格式 (Pydantic)

* schemas → routes（有格式才能寫 endpoint）

5. routes.py (或 routers/)
   └── 寫 API endpoints
   └── 用 schemas 驗證資料
   └── 用 models 操作 DB

* routes → main（有 router 才能組裝）

6. main.py
   └── 串接 database、routes
   └── create_all()
   └── include_router()

7. 測試
   └── 開 /docs 手動測試
   └── 或寫 pytest