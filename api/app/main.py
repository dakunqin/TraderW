import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.migrate import migrate
from app.db.session import get_engine


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    logger = logging.getLogger("uvicorn.error")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.on_event("startup")
    def startup():
        engine = get_engine()
        logger.info("DATABASE_URL=%s", str(engine.url))
        Base.metadata.create_all(bind=engine)
        migrate(engine)

    @app.get("/health")
    def health():
        return {"ok": True}

    dist_dir = Path(__file__).resolve().parents[1] / "web" / "dist"
    index_file = dist_dir / "index.html"

    if index_file.exists():

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str):
            if full_path.startswith("api/") or full_path == "api":
                raise HTTPException(status_code=404)
            p = (dist_dir / full_path).resolve()
            if p.is_file() and str(p).startswith(str(dist_dir.resolve())):
                return FileResponse(str(p))
            return FileResponse(str(index_file))

    return app


app = create_app()
