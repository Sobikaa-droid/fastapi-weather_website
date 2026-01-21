from fastapi import Request
import httpx


def process_weather_data(request: Request, data: dict, query: str, temp_scale: str = "temp_c"):
    local_time_is_full = len(data["location"]["localtime"]) == 16
    date_string = data["location"]["localtime"][:10] if local_time_is_full else ""
    time_string = data["location"]["localtime"][11:] if local_time_is_full else ""

    current_day_hours_list = data["forecast"]["forecastday"][0]["hour"]
    current_hour = int(time_string[0:2]) if time_string and ':' in time_string else 0
    hours_to_display = 8
    recent_hours_list = current_day_hours_list[current_hour+1:hours_to_display*3:3]

    if len(recent_hours_list) < hours_to_display:
        next_day_hours_list = data["forecast"]["forecastday"][1]["hour"]
        next_day_recent_hours_list = next_day_hours_list[0:(hours_to_display-len(recent_hours_list))*3:3]
        recent_hours_list = recent_hours_list + next_day_recent_hours_list

    if temp_scale not in ["temp_c", "temp_f"]:
        temp_scale = "temp_c"

    return {
        "request": request,
        "search_query": query,
        "location": data["location"]["name"],
        "country": data["location"]["country"],
        "time": time_string,
        "date": date_string,
        "recent_hours": recent_hours_list,
        "condition": data["current"]["condition"]["text"],
        "humidity": data["current"]["humidity"],
        "wind": data["current"]["wind_kph"],
        "precipitation": data["current"]["precip_in"],
        "temp_scale": temp_scale,
        "temperature": data["current"][temp_scale],
        "forecast_days_list": data["forecast"]["forecastday"],
        "error": None,
    }


def process_error_data(request: Request, query: str, error_type: str, error_details=None):
    """Handle different types of errors and return appropriate context"""
    error_messages = {
        "invalid_city": f"City '{query}' not found. Please check the spelling.",
        "http_error": f"Weather service error (HTTP {error_details}). Please try again later.",
        "network_error": "Cannot connect to weather service. Please check your internet connection.",
        "data_error": "Received unexpected data format from weather service.",
        "timeout": "Request timed out. Please try again.",
    }

    error_msg = error_messages.get(error_type, "An unexpected error occurred.")

    return {
        "request": request,
        "search_query": query,
        "error": error_msg,
        "location": query,
        "country": "",
        "time": "",
        "date": "",
        "recent_hours": [],
        "condition": "",
        "humidity": 0,
        "wind": 0,
        "precipitation": 0,
        "temperature": 0,
        "forecast_days_list": [],
    }


async def get_ip_info(ip_address: str):
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()

    return {
        "ip": ip_address,
        "city": data.get("city"),
        "region": data.get("regionName"),
    }
