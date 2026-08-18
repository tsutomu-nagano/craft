from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.analyses import router as analyses_router
from app.api.reviews import router as reviews_router
from app.mcp.server import mcp, mcp_app
from app.repositories.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="craft",
    description="機械判読性AIプラットフォーム",
    lifespan=lifespan,
)

app.include_router(analyses_router)
app.include_router(reviews_router)
app.router.routes.extend(mcp_app.routes)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse("frontend/index.html")
