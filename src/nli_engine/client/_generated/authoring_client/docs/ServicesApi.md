# nli_engine.client.\_generated.authoring_client.ServicesApi

All URIs are relative to _http://localhost:8080_

| Method                                                                | HTTP request                                        | Description                                      |
| --------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------ |
| [**add_air_quality_service**](ServicesApi.md#add_air_quality_service) | **POST** /sessions/{sessionId}/services/air-quality | Add air quality service to the session protocol  |
| [**add_health_service**](ServicesApi.md#add_health_service)           | **POST** /sessions/{sessionId}/services/health      | Add health service to the session protocol       |
| [**add_location_service**](ServicesApi.md#add_location_service)       | **POST** /sessions/{sessionId}/services/location    | Add location service to the session protocol     |
| [**add_weather_service**](ServicesApi.md#add_weather_service)         | **POST** /sessions/{sessionId}/services/weather     | Add weather service to the session protocol      |
| [**get_service_roles**](ServicesApi.md#get_service_roles)             | **GET** /sessions/{sessionId}/services              | Get connected services from the session protocol |

# **add_air_quality_service**

> SessionMutationResponse add_air_quality_service(session_id, air_quality_service_request)

Add air quality service to the session protocol

Adds a background air quality data service to the session protocol. primaryDeviceRoleName must match an existing primary device role. roleName defaults to "Air Quality" if omitted. The service collects ambient air quality readings from an online API.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.air_quality_service_request import AirQualityServiceRequest
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = nli_engine.client._generated.authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with nli_engine.client._generated.authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nli_engine.client._generated.authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    air_quality_service_request = {"roleName":"Local Air Quality","primaryDeviceRoleName":"User Phone"} # AirQualityServiceRequest | Air quality service configuration payload.

    try:
        # Add air quality service to the session protocol
        api_response = api_instance.add_air_quality_service(session_id, air_quality_service_request)
        print("The response of ServicesApi->add_air_quality_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_air_quality_service: %s\n" % e)
```

### Parameters

| Name                            | Type                                                        | Description                                    | Notes |
| ------------------------------- | ----------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                  | **str**                                                     | Session identifier returned by POST /sessions. |
| **air_quality_service_request** | [**AirQualityServiceRequest**](AirQualityServiceRequest.md) | Air quality service configuration payload.     |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                       | Response headers |
| ----------- | ----------------------------------------------------------------- | ---------------- |
| **201**     | Air quality service added                                         | -                |
| **400**     | Missing or invalid request body, or primary device not configured | -                |
| **404**     | Session id not found.                                             | -                |
| **0**       | Unexpected server error.                                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_health_service**

> SessionMutationResponse add_health_service(session_id, health_service_request)

Add health service to the session protocol

Adds a background health data service to the session protocol. primaryDeviceRoleName must match an existing primary device role. roleName defaults to "Health" if omitted. The service reads health data from the platform health framework (Apple Health or Google Fit).

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.health_service_request import HealthServiceRequest
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = nli_engine.client._generated.authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with nli_engine.client._generated.authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nli_engine.client._generated.authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    health_service_request = {"roleName":"Device Health","primaryDeviceRoleName":"User Phone"} # HealthServiceRequest | Health service configuration payload.

    try:
        # Add health service to the session protocol
        api_response = api_instance.add_health_service(session_id, health_service_request)
        print("The response of ServicesApi->add_health_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_health_service: %s\n" % e)
```

### Parameters

| Name                       | Type                                                | Description                                    | Notes |
| -------------------------- | --------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**             | **str**                                             | Session identifier returned by POST /sessions. |
| **health_service_request** | [**HealthServiceRequest**](HealthServiceRequest.md) | Health service configuration payload.          |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                       | Response headers |
| ----------- | ----------------------------------------------------------------- | ---------------- |
| **201**     | Health service added                                              | -                |
| **400**     | Missing or invalid request body, or primary device not configured | -                |
| **404**     | Session id not found.                                             | -                |
| **0**       | Unexpected server error.                                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_location_service**

> SessionMutationResponse add_location_service(session_id, location_service_request)

Add location service to the session protocol

Adds a background location service to the session protocol. primaryDeviceRoleName must match an existing primary device role. roleName defaults to "Location" if omitted. accuracy controls the GPS accuracy level; distance sets the minimum movement threshold in meters; notificationTitle and notificationMessage configure the background location notification on Android.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.location_service_request import LocationServiceRequest
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = nli_engine.client._generated.authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with nli_engine.client._generated.authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nli_engine.client._generated.authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    location_service_request = {"roleName":"User Location","primaryDeviceRoleName":"User Phone","accuracy":"balanced","distance":10.0,"interval":{"seconds":60},"notificationTitle":"Tracking active","notificationMessage":"Location tracking is running.","notificationDescription":"Tap to return to the app.","notificationIconName":"ic_notification","notificationOnTapBringToFront":false} # LocationServiceRequest | Location service configuration payload.

    try:
        # Add location service to the session protocol
        api_response = api_instance.add_location_service(session_id, location_service_request)
        print("The response of ServicesApi->add_location_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_location_service: %s\n" % e)
```

### Parameters

| Name                         | Type                                                    | Description                                    | Notes |
| ---------------------------- | ------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**               | **str**                                                 | Session identifier returned by POST /sessions. |
| **location_service_request** | [**LocationServiceRequest**](LocationServiceRequest.md) | Location service configuration payload.        |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                       | Response headers |
| ----------- | ----------------------------------------------------------------- | ---------------- |
| **201**     | Location service added                                            | -                |
| **400**     | Missing or invalid request body, or primary device not configured | -                |
| **404**     | Session id not found.                                             | -                |
| **0**       | Unexpected server error.                                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_weather_service**

> SessionMutationResponse add_weather_service(session_id, weather_service_request)

Add weather service to the session protocol

Adds a background weather data service to the session protocol. primaryDeviceRoleName must match an existing primary device role. roleName defaults to "Weather" if omitted. The service collects ambient weather data from an online API.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.models.weather_service_request import WeatherServiceRequest
from nli_engine.client._generated.authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = nli_engine.client._generated.authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with nli_engine.client._generated.authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nli_engine.client._generated.authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    weather_service_request = {"roleName":"Local Weather","primaryDeviceRoleName":"User Phone"} # WeatherServiceRequest | Weather service configuration payload.

    try:
        # Add weather service to the session protocol
        api_response = api_instance.add_weather_service(session_id, weather_service_request)
        print("The response of ServicesApi->add_weather_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_weather_service: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                                    | Notes |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**              | **str**                                               | Session identifier returned by POST /sessions. |
| **weather_service_request** | [**WeatherServiceRequest**](WeatherServiceRequest.md) | Weather service configuration payload.         |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                       | Response headers |
| ----------- | ----------------------------------------------------------------- | ---------------- |
| **201**     | Weather service added                                             | -                |
| **400**     | Missing or invalid request body, or primary device not configured | -                |
| **404**     | Session id not found.                                             | -                |
| **0**       | Unexpected server error.                                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_service_roles**

> ServiceRolesResponse get_service_roles(session_id)

Get connected services from the session protocol

Returns connected services currently configured in the session protocol, including role name and serialized service payload. Each service object contains a \_\_type discriminator identifying the concrete CARP service type.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.service_roles_response import ServiceRolesResponse
from nli_engine.client._generated.authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = nli_engine.client._generated.authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with nli_engine.client._generated.authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nli_engine.client._generated.authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.

    try:
        # Get connected services from the session protocol
        api_response = api_instance.get_service_roles(session_id)
        print("The response of ServicesApi->get_service_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->get_service_roles: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                    | Notes |
| -------------- | ------- | ---------------------------------------------- | ----- |
| **session_id** | **str** | Session identifier returned by POST /sessions. |

### Return type

[**ServiceRolesResponse**](ServiceRolesResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                 | Response headers |
| ----------- | --------------------------- | ---------------- |
| **200**     | Connected services returned | -                |
| **400**     | Missing session id          | -                |
| **404**     | Session id not found.       | -                |
| **0**       | Unexpected server error.    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
