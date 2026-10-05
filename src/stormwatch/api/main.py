# FastAPI application entry point
import logging
import os
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from stormwatch.api.routes.health import (
    router as health_router,
)
from stormwatch.api.routes.public_weather import router as public_weather_router
from stormwatch.api.routes.risk import (
    router as risk_router,
)
from stormwatch.api.routes.weather import (
    router as weather_router,
)

app = FastAPI(
    title="StormWatch API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5174,http://127.0.0.1:5174",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_weather_response_timing(request: Request, call_next):
    if not request.url.path.startswith("/api/weather"):
        return await call_next(request)
    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        logging.getLogger("stormwatch.api.requests").info(
            "Weather API response completed",
            extra={
                "event": "weather_response_timing",
                "method": request.method,
                "route": getattr(route, "path", "/api/weather/unknown"),
                "status_code": status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            },
        )


app.include_router(
    health_router
)

app.include_router(
    weather_router
)

app.include_router(
    risk_router
)

app.include_router(public_weather_router)
