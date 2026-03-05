"""FastAPI application entry point with exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.routers.analyze import router as analyze_router
from app.routers.risk import router as risk_router
from app.routers.screener import router as screener_router

app = FastAPI(title="US Stock Candle Analysis")

app.include_router(analyze_router)
app.include_router(risk_router)
app.include_router(screener_router)


@app.get("/")
def root() -> FileResponse:
    """Serve the main HTML page."""
    return FileResponse("static/index.html")


@app.get("/screener")
def screener_page() -> FileResponse:
    """Serve the screener HTML page."""
    return FileResponse("static/screener.html")


# Mount static files AFTER routers to avoid conflicts
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(TickerNotFoundError)
async def ticker_not_found_handler(
    request: Request, exc: TickerNotFoundError
) -> JSONResponse:
    """Handle TickerNotFoundError with 400 status."""
    return JSONResponse(
        status_code=400,
        content={"detail": f"'{exc}' は有効な株式銘柄ではありません。"},
    )


@app.exception_handler(TickerNotEquityError)
async def ticker_not_equity_handler(
    request: Request, exc: TickerNotEquityError
) -> JSONResponse:
    """Handle TickerNotEquityError with 400 status."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": f"'{exc.ticker}' は株式ではありません（種別: {exc.quote_type}）。"
        },
    )


@app.exception_handler(DataFetchError)
async def data_fetch_error_handler(
    request: Request, exc: DataFetchError
) -> JSONResponse:
    """Handle DataFetchError with 500 status."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "データの取得中にエラーが発生しました。しばらく経ってから再試行してください。"
        },
    )
