from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.analyses import router as analyses_router
from app.api.reviews import router as reviews_router
from app.mcp.server import mcp_app
from app.repositories.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="craft",
    description="機械判読性AIプラットフォーム",
    lifespan=lifespan,
)

app.include_router(analyses_router)
app.include_router(reviews_router)
app.mount("/mcp", mcp_app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
