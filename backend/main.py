from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database.connection import Base, SessionLocal, engine
from routes import api_router
from services.graph_service import bootstrap_graph_from_db
from utils.logger import get_logger

# Ensure models are imported so SQLAlchemy can discover tables
from models.invoice import Invoice  # noqa: F401
from models.invoice_item import InvoiceItem  # noqa: F401

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("cipherlink_startup", extra={"environment": settings.environment})
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        bootstrap_graph_from_db(db)
    yield
    logger.info("cipherlink_shutdown")


app = FastAPI(
    title="CipherLink API",
    version="0.1.0",
    description="Multi-tier supply chain fraud detection foundation",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"message": "CipherLink backend is online"}
