# authoring_client.ServicesApi

All URIs are relative to _http://localhost:8080_

| Method                                                                | HTTP request                                        | Description                                      |
| --------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------ |
| [**add_air_quality_service**](ServicesApi.md#add_air_quality_service) | **POST** /sessions/{sessionId}/services/air-quality | Add air quality service to the session protocol  |
| [**add_health_service**](ServicesApi.md#add_health_service)           | **POST** /sessions/{sessionId}/services/health      | Add health service to the session protocol       |
| [**add_location_service**](ServicesApi.md#add_location_service)       | **POST** /sessions/{sessionId}/services/location    | Add location service to the session protocol     |
| [**add_weather_service**](ServicesApi.md#add_weather_service)         | **POST** /sessions/{sessionId}/services/weather     | Add weather service to the session protocol      |
| [**get_service_roles**](ServicesApi.md#get_service_roles)             | **GET** /sessions/{sessionId}/services              | Get connected services from the session protocol |

# **add_air_quality_service**

> DataEndpointResponse add_air_quality_service(session_id, primary_device_role_name, role_name=role_name)

Add air quality service to the session protocol

Adds air quality service as a connected device. Requires a configured primary device.

### Example

```python
import authoring_client
from authoring_client.models.data_endpoint_response import DataEndpointResponse
from authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    primary_device_role_name = 'User Phone' # str | Role name of the primary device this service is connected to.
    role_name = 'Local Air Quality' # str | Optional role name for the air quality service. (optional)

    try:
        # Add air quality service to the session protocol
        api_response = api_instance.add_air_quality_service(session_id, primary_device_role_name, role_name=role_name)
        print("The response of ServicesApi->add_air_quality_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_air_quality_service: %s\n" % e)
```

### Parameters

| Name                         | Type    | Description                                                   | Notes      |
| ---------------------------- | ------- | ------------------------------------------------------------- | ---------- |
| **session_id**               | **str** | Session id returned by POST /protocol/new.                    |
| **primary_device_role_name** | **str** | Role name of the primary device this service is connected to. |
| **role_name**                | **str** | Optional role name for the air quality service.               | [optional] |

### Return type

[**DataEndpointResponse**](DataEndpointResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                                               | Response headers |
| ----------- | --------------------------------------------------------- | ---------------- |
| **200**     | Air quality service added                                 | -                |
| **400**     | Missing query parameters or primary device not configured | -                |
| **404**     | Session id not found                                      | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_health_service**

> DataEndpointResponse add_health_service(session_id, primary_device_role_name, role_name=role_name)

Add health service to the session protocol

Adds health service as a connected device. Requires a configured primary device.

### Example

```python
import authoring_client
from authoring_client.models.data_endpoint_response import DataEndpointResponse
from authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    primary_device_role_name = 'User Phone' # str | Role name of the primary device this service is connected to.
    role_name = 'Device Health' # str | Optional role name for the health service. (optional)

    try:
        # Add health service to the session protocol
        api_response = api_instance.add_health_service(session_id, primary_device_role_name, role_name=role_name)
        print("The response of ServicesApi->add_health_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_health_service: %s\n" % e)
```

### Parameters

| Name                         | Type    | Description                                                   | Notes      |
| ---------------------------- | ------- | ------------------------------------------------------------- | ---------- |
| **session_id**               | **str** | Session id returned by POST /protocol/new.                    |
| **primary_device_role_name** | **str** | Role name of the primary device this service is connected to. |
| **role_name**                | **str** | Optional role name for the health service.                    | [optional] |

### Return type

[**DataEndpointResponse**](DataEndpointResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                                               | Response headers |
| ----------- | --------------------------------------------------------- | ---------------- |
| **200**     | Health service added                                      | -                |
| **400**     | Missing query parameters or primary device not configured | -                |
| **404**     | Session id not found                                      | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_location_service**

> DataEndpointResponse add_location_service(session_id, location_service_request)

Add location service to the session protocol

Adds location service as a connected device. Requires a configured primary device.

### Example

```python
import authoring_client
from authoring_client.models.data_endpoint_response import DataEndpointResponse
from authoring_client.models.location_service_request import LocationServiceRequest
from authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
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

| Name                         | Type                                                    | Description                                | Notes |
| ---------------------------- | ------------------------------------------------------- | ------------------------------------------ | ----- |
| **session_id**               | **str**                                                 | Session id returned by POST /protocol/new. |
| **location_service_request** | [**LocationServiceRequest**](LocationServiceRequest.md) | Location service configuration payload.    |

### Return type

[**DataEndpointResponse**](DataEndpointResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                                | Response headers |
| ----------- | -------------------------------------------------------------------------- | ---------------- |
| **200**     | Location service added                                                     | -                |
| **400**     | Missing query parameters, invalid values, or primary device not configured | -                |
| **404**     | Session id not found                                                       | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_weather_service**

> DataEndpointResponse add_weather_service(session_id, primary_device_role_name, role_name=role_name)

Add weather service to the session protocol

Adds weather service as a connected device. Requires a configured primary device.

### Example

```python
import authoring_client
from authoring_client.models.data_endpoint_response import DataEndpointResponse
from authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    primary_device_role_name = 'User Phone' # str | Role name of the primary device this service is connected to.
    role_name = 'Local Weather' # str | Optional role name for the weather service. (optional)

    try:
        # Add weather service to the session protocol
        api_response = api_instance.add_weather_service(session_id, primary_device_role_name, role_name=role_name)
        print("The response of ServicesApi->add_weather_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->add_weather_service: %s\n" % e)
```

### Parameters

| Name                         | Type    | Description                                                   | Notes      |
| ---------------------------- | ------- | ------------------------------------------------------------- | ---------- |
| **session_id**               | **str** | Session id returned by POST /protocol/new.                    |
| **primary_device_role_name** | **str** | Role name of the primary device this service is connected to. |
| **role_name**                | **str** | Optional role name for the weather service.                   | [optional] |

### Return type

[**DataEndpointResponse**](DataEndpointResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                                               | Response headers |
| ----------- | --------------------------------------------------------- | ---------------- |
| **200**     | Weather service added                                     | -                |
| **400**     | Missing query parameters or primary device not configured | -                |
| **404**     | Session id not found                                      | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_service_roles**

> ServiceRolesResponse get_service_roles(session_id)

Get connected services from the session protocol

Returns connected services currently configured in the session protocol, including role name and serialized service payload.

### Example

```python
import authoring_client
from authoring_client.models.service_roles_response import ServiceRolesResponse
from authoring_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = authoring_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with authoring_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = authoring_client.ServicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.

    try:
        # Get connected services from the session protocol
        api_response = api_instance.get_service_roles(session_id)
        print("The response of ServicesApi->get_service_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->get_service_roles: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                | Notes |
| -------------- | ------- | ------------------------------------------ | ----- |
| **session_id** | **str** | Session id returned by POST /protocol/new. |

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
| **404**     | Session id not found        | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
