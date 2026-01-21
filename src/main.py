from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import uvicorn
import httpx
import os
import logging

from .dependencies import main_deps, jinja_filters
from . import database
from .config import settings


load_dotenv()

# def create_tables():
#     database.Base.metadata.create_all(bind=database.async_engine)


def include_router(app: FastAPI):
    pass


# REPLACED BY NGINX
def configure_staticfiles(app: FastAPI):
    # app.mount("/static", StaticFiles(directory="static"), name="static")
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.async_engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    yield
    await database.async_engine.dispose()


def start_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        version="1.0.0",
        docs_url="/docs" if settings.debug else None
    )
    include_router(app)
    configure_staticfiles(app)
    return app


app = start_application()
security = HTTPBearer()

# Jinja
templates = Jinja2Templates(directory="templates")
templates.env.filters["strptime"] = jinja_filters.strptime_filter
templates.env.filters["strftime"] = jinja_filters.strftime_filter
templates.env.filters["url_with"] = jinja_filters.url_with_params

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Use __name__ for module name


@app.get("/", response_class=HTMLResponse)
async def home(
        request: Request,
        city_name: str = Query("", description="Search query"),
        temp_scale: str = Query("temp_c", description="Temperature scale")
):
    if not city_name:
        # real_ip = request.headers.get("X-Real-IP")
        temp_ip = "156.33.241.5"  # REPLACE WITH REAL_IP IN PRODUCTION
        ip_info = await main_deps.get_ip_info(temp_ip)
        city_name = ip_info["city"]

    params = {
        'key': os.getenv("WEATHER_API_KEY"),
        'q': city_name,
        'days': 6,
        'aqi': "no",
        "alert": "no",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("http://api.weatherapi.com/v1/forecast.json", params=params)

            if response.status_code == 400:
                logger.error(f"City not found")
                context = main_deps.process_error_data(request, error_type="invalid_city", query=city_name)
                return templates.TemplateResponse("404.html", context)

            response.raise_for_status()
            data = response.json()
            context = main_deps.process_weather_data(request, data=data, query=city_name, temp_scale=temp_scale)
            return templates.TemplateResponse("home.html", context)

    except httpx.HTTPStatusError as error:
        logger.error(f"HTTP error from WeatherAPI: {error}")
        context = main_deps.process_error_data(request, query=city_name, error_type="http_error", error_details=error)
        return templates.TemplateResponse("home.html", context)

    except httpx.TimeoutException:
        logger.error("WeatherAPI request timeout")
        context = main_deps.process_error_data(request, query=city_name, error_type="timeout")
        return templates.TemplateResponse("home.html", context)

    except httpx.RequestError as error:
        logger.error(f"Request error: {error}")
        context = main_deps.process_error_data(request, query=city_name, error_type="request_error", error_details=error)
        return templates.TemplateResponse("home.html", context)

    except (KeyError, ValueError, TypeError) as error:
        logger.error(f"Unexpected error: {error}")
        context = main_deps.process_error_data(request, query=city_name, error_type="data_error", error_details=error)
        return templates.TemplateResponse("home.html", context)


# @app.get("/", response_class=HTMLResponse)
# def home(request: Request, alert: str = None):
#     context = {
#         "alert": alert,
#     }
#     return templates.TemplateResponse(request, "home.html", context)


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
