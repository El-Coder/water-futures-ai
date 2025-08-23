from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from api.routes import water_futures, forecasts, trading, news, embeddings
from config.settings import settings
from services.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    
app = FastAPI(
    title="Water Futures AI API",
    description="API for water futures trading, forecasting, and analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(water_futures.router, prefix="/api/v1/water-futures", tags=["Water Futures"])
app.include_router(forecasts.router, prefix="/api/v1/forecasts", tags=["Forecasts"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["Trading"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(embeddings.router, prefix="/api/v1/embeddings", tags=["Embeddings"])

@app.get("/")
async def root():
    return {"message": "Water Futures AI API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )