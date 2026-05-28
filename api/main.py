# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from data.database import init_db
from api.routes import recognize, recommend, profile, history
from api.dependencies import get_recognizer, get_predictor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時執行：初始化 DB + 預載模型（避免第一個 request 等很久）
    init_db()
    get_recognizer()
    get_predictor()
    print("✅ 模型載入完成，伺服器就緒")
    yield
    # 關閉時可做清理（目前不需要）

app = FastAPI(
    title="你的專屬菜單生成器",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(recognize.router)
app.include_router(recommend.router)
app.include_router(profile.router)
app.include_router(history.router)

# 本機啟動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)