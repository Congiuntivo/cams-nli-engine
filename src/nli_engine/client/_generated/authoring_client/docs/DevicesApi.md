# nli_engine.client.\_generated.authoring_client.DevicesApi

All URIs are relative to _http://localhost:8080_

| Method                                                         | HTTP request                                     | Description                                     |
| -------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------- |
| [**add_e_sense_device**](DevicesApi.md#add_e_sense_device)     | **POST** /sessions/{sessionId}/devices/e-sense   | Add an eSense device to the session protocol    |
| [**add_movesense_device**](DevicesApi.md#add_movesense_device) | **POST** /sessions/{sessionId}/devices/movesense | Add a Movesense device to the session protocol  |
| [**add_movisens_device**](DevicesApi.md#add_movisens_device)   | **POST** /sessions/{sessionId}/devices/movisens  | Add a Movisens device to the session protocol   |
| [**add_polar_device**](DevicesApi.md#add_polar_device)         | **POST** /sessions/{sessionId}/devices/polar     | Add a Polar device to the session protocol      |
| [**get_device_roles**](DevicesApi.md#get_device_roles)         | **GET** /sessions/{sessionId}/devices            | Get connected devices from the session protocol |

# **add_e_sense_device**

> SessionMutationResponse add_e_sense_device(session_id, e_sense_device_request)

Add an eSense device to the session protocol

Adds a connected eSense hearing device to the session protocol. primaryDeviceRoleName must match an existing primary device role — if it does not, an unfulfilled critical requirement is recorded. roleName defaults to "eSense" if omitted. samplingRate sets the sensor sampling frequency in Hz.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.e_sense_device_request import ESenseDeviceRequest
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
    api_instance = nli_engine.client._generated.authoring_client.DevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    e_sense_device_request = {"roleName":"Left Earbud","primaryDeviceRoleName":"User Phone","isOptional":false,"samplingRate":10} # ESenseDeviceRequest | eSense device payload.

    try:
        # Add an eSense device to the session protocol
        api_response = api_instance.add_e_sense_device(session_id, e_sense_device_request)
        print("The response of DevicesApi->add_e_sense_device:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->add_e_sense_device: %s\n" % e)
```

### Parameters

| Name                       | Type                                              | Description                                    | Notes |
| -------------------------- | ------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**             | **str**                                           | Session identifier returned by POST /sessions. |
| **e_sense_device_request** | [**ESenseDeviceRequest**](ESenseDeviceRequest.md) | eSense device payload.                         |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                              | Response headers |
| ----------- | ------------------------------------------------------------------------ | ---------------- |
| **201**     | eSense device added                                                      | -                |
| **400**     | Missing or invalid request body values, or primary device not configured | -                |
| **404**     | Session id not found.                                                    | -                |
| **0**       | Unexpected server error.                                                 | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_movesense_device**

> SessionMutationResponse add_movesense_device(session_id, movesense_device_request)

Add a Movesense device to the session protocol

Adds a connected Movesense wearable sensor to the session protocol. primaryDeviceRoleName must match an existing primary device role — if it does not, an unfulfilled critical requirement is recorded. roleName defaults to "Movesense" if omitted.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.movesense_device_request import MovesenseDeviceRequest
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
    api_instance = nli_engine.client._generated.authoring_client.DevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    movesense_device_request = {"roleName":"Chest Sensor","primaryDeviceRoleName":"User Phone","isOptional":false} # MovesenseDeviceRequest | Movesense device payload.

    try:
        # Add a Movesense device to the session protocol
        api_response = api_instance.add_movesense_device(session_id, movesense_device_request)
        print("The response of DevicesApi->add_movesense_device:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->add_movesense_device: %s\n" % e)
```

### Parameters

| Name                         | Type                                                    | Description                                    | Notes |
| ---------------------------- | ------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**               | **str**                                                 | Session identifier returned by POST /sessions. |
| **movesense_device_request** | [**MovesenseDeviceRequest**](MovesenseDeviceRequest.md) | Movesense device payload.                      |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                              | Response headers |
| ----------- | ------------------------------------------------------------------------ | ---------------- |
| **201**     | Movesense device added                                                   | -                |
| **400**     | Missing or invalid request body values, or primary device not configured | -                |
| **404**     | Session id not found.                                                    | -                |
| **0**       | Unexpected server error.                                                 | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_movisens_device**

> SessionMutationResponse add_movisens_device(session_id, movisens_device_request)

Add a Movisens device to the session protocol

Adds a connected Movisens wearable sensor to the session protocol. primaryDeviceRoleName must match an existing primary device role — if it does not, an unfulfilled critical requirement is recorded. roleName defaults to "Movisens" if omitted. sensorLocation must be one of the enum values in the MovisensDeviceRequest schema if provided.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.movisens_device_request import MovisensDeviceRequest
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
    api_instance = nli_engine.client._generated.authoring_client.DevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    movisens_device_request = {"roleName":"Torso Sensor","primaryDeviceRoleName":"User Phone","sensorLocation":"Chest","sex":"Male","height":178,"weight":78,"age":25} # MovisensDeviceRequest | Movisens device payload.

    try:
        # Add a Movisens device to the session protocol
        api_response = api_instance.add_movisens_device(session_id, movisens_device_request)
        print("The response of DevicesApi->add_movisens_device:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->add_movisens_device: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                                    | Notes |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**              | **str**                                               | Session identifier returned by POST /sessions. |
| **movisens_device_request** | [**MovisensDeviceRequest**](MovisensDeviceRequest.md) | Movisens device payload.                       |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                              | Response headers |
| ----------- | ------------------------------------------------------------------------ | ---------------- |
| **201**     | Movisens device added                                                    | -                |
| **400**     | Missing or invalid request body values, or primary device not configured | -                |
| **404**     | Session id not found.                                                    | -                |
| **0**       | Unexpected server error.                                                 | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_polar_device**

> SessionMutationResponse add_polar_device(session_id, polar_device_request)

Add a Polar device to the session protocol

Adds a connected Polar heart rate monitor to the session protocol. primaryDeviceRoleName must match an existing primary device role — if it does not, an unfulfilled critical requirement is recorded. roleName defaults to "Polar" if omitted. namePrefix is used to identify the specific Polar device by its Bluetooth advertisement name prefix.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.polar_device_request import PolarDeviceRequest
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
    api_instance = nli_engine.client._generated.authoring_client.DevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    polar_device_request = {"roleName":"Polar Chest Sensor","primaryDeviceRoleName":"User Phone","isOptional":false,"namePrefix":"Polar"} # PolarDeviceRequest | Polar device payload.

    try:
        # Add a Polar device to the session protocol
        api_response = api_instance.add_polar_device(session_id, polar_device_request)
        print("The response of DevicesApi->add_polar_device:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->add_polar_device: %s\n" % e)
```

### Parameters

| Name                     | Type                                            | Description                                    | Notes |
| ------------------------ | ----------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**           | **str**                                         | Session identifier returned by POST /sessions. |
| **polar_device_request** | [**PolarDeviceRequest**](PolarDeviceRequest.md) | Polar device payload.                          |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                              | Response headers |
| ----------- | ------------------------------------------------------------------------ | ---------------- |
| **201**     | Polar device added                                                       | -                |
| **400**     | Missing or invalid request body values, or primary device not configured | -                |
| **404**     | Session id not found.                                                    | -                |
| **0**       | Unexpected server error.                                                 | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_roles**

> DeviceRolesResponse get_device_roles(session_id)

Get connected devices from the session protocol

Returns connected devices currently configured in the session protocol, including role name and serialized device payload. Each device object contains a \_\_type discriminator identifying the concrete CARP device type.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.device_roles_response import DeviceRolesResponse
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
    api_instance = nli_engine.client._generated.authoring_client.DevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.

    try:
        # Get connected devices from the session protocol
        api_response = api_instance.get_device_roles(session_id)
        print("The response of DevicesApi->get_device_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_roles: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                    | Notes |
| -------------- | ------- | ---------------------------------------------- | ----- |
| **session_id** | **str** | Session identifier returned by POST /sessions. |

### Return type

[**DeviceRolesResponse**](DeviceRolesResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                | Response headers |
| ----------- | -------------------------- | ---------------- |
| **200**     | Connected devices returned | -                |
| **400**     | Missing session id         | -                |
| **404**     | Session id not found.      | -                |
| **0**       | Unexpected server error.   | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
