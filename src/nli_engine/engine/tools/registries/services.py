from nli_engine.client._generated.authoring_client import (
    AirQualityServiceRequest,
    HealthServiceRequest,
    LocationServiceRequest,
    ServicesApi,
    WeatherServiceRequest,
)
from nli_engine.engine.tools.spec import ToolSpec

SERVICES_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_air_quality_service",
        api_class=ServicesApi,
        method="add_air_quality_service",
        request_model=AirQualityServiceRequest,
        description="Add an air quality sensor service.",
    ),
    ToolSpec(
        name="add_health_service",
        api_class=ServicesApi,
        method="add_health_service",
        request_model=HealthServiceRequest,
        description="Add a health data service.",
    ),
    ToolSpec(
        name="add_weather_service",
        api_class=ServicesApi,
        method="add_weather_service",
        request_model=WeatherServiceRequest,
        description="Add a weather data service.",
    ),
    ToolSpec(
        name="add_location_service",
        api_class=ServicesApi,
        method="add_location_service",
        request_model=LocationServiceRequest,
        description="Add a GPS/location service.",
    ),
]
