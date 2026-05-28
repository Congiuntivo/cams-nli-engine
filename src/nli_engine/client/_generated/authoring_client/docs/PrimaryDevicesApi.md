# nli_engine.client.\_generated.authoring_client.PrimaryDevicesApi

All URIs are relative to _http://localhost:8080_

| Method                                                                                    | HTTP request                                               | Description                                              |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------- |
| [**add_smartphone_primary_device**](PrimaryDevicesApi.md#add_smartphone_primary_device)   | **POST** /sessions/{sessionId}/primary-devices/smartphone  | Add a smartphone primary device to the session protocol  |
| [**add_web_browser_primary_device**](PrimaryDevicesApi.md#add_web_browser_primary_device) | **POST** /sessions/{sessionId}/primary-devices/web-browser | Add a web browser primary device to the session protocol |
| [**get_primary_devices**](PrimaryDevicesApi.md#get_primary_devices)                       | **GET** /sessions/{sessionId}/primary-devices              | Get primary devices from the session protocol            |

# **add_smartphone_primary_device**

> SessionMutationResponse add_smartphone_primary_device(session_id, primary_device_role_request)

Add a smartphone primary device to the session protocol

Adds a Smartphone as the primary device in the session protocol. A primary device must be added before tasks and triggers can be added. roleName defaults to "Smartphone" if omitted. Adding a primary device fulfills the critical requirement for at least one primary device.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.primary_device_role_request import PrimaryDeviceRoleRequest
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
    api_instance = nli_engine.client._generated.authoring_client.PrimaryDevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    primary_device_role_request = {"roleName":"User Phone"} # PrimaryDeviceRoleRequest | Optional role name for the primary smartphone.

    try:
        # Add a smartphone primary device to the session protocol
        api_response = api_instance.add_smartphone_primary_device(session_id, primary_device_role_request)
        print("The response of PrimaryDevicesApi->add_smartphone_primary_device:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrimaryDevicesApi->add_smartphone_primary_device: %s\n" % e)
```

### Parameters

| Name                            | Type                                                        | Description                                    | Notes |
| ------------------------------- | ----------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                  | **str**                                                     | Session identifier returned by POST /sessions. |
| **primary_device_role_request** | [**PrimaryDeviceRoleRequest**](PrimaryDeviceRoleRequest.md) | Optional role name for the primary smartphone. |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                        | Response headers |
| ----------- | ------------------------------------------------------------------ | ---------------- |
| **201**     | Primary device added                                               | -                |
| **400**     | Missing session id, invalid payload, or incompatible protocol type | -                |
| **404**     | Session id not found.                                              | -                |
| **0**       | Unexpected server error.                                           | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_web_browser_primary_device**

> SessionMutationResponse add_web_browser_primary_device(session_id, primary_device_role_request)

Add a web browser primary device to the session protocol

Adds a WebBrowser as the primary device in the session protocol. A primary device must be added before tasks and triggers can be added. roleName defaults to "Web Browser" if omitted. Adding a primary device fulfills the critical requirement for at least one primary device.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.primary_device_role_request import PrimaryDeviceRoleRequest
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
    api_instance = nli_engine.client._generated.authoring_client.PrimaryDevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    primary_device_role_request = {"roleName":"Participant Browser"} # PrimaryDeviceRoleRequest | Optional role name for the primary web browser.

    try:
        # Add a web browser primary device to the session protocol
        api_response = api_instance.add_web_browser_primary_device(session_id, primary_device_role_request)
        print("The response of PrimaryDevicesApi->add_web_browser_primary_device:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrimaryDevicesApi->add_web_browser_primary_device: %s\n" % e)
```

### Parameters

| Name                            | Type                                                        | Description                                     | Notes |
| ------------------------------- | ----------------------------------------------------------- | ----------------------------------------------- | ----- |
| **session_id**                  | **str**                                                     | Session identifier returned by POST /sessions.  |
| **primary_device_role_request** | [**PrimaryDeviceRoleRequest**](PrimaryDeviceRoleRequest.md) | Optional role name for the primary web browser. |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                        | Response headers |
| ----------- | ------------------------------------------------------------------ | ---------------- |
| **201**     | Primary device added                                               | -                |
| **400**     | Missing session id, invalid payload, or incompatible protocol type | -                |
| **404**     | Session id not found.                                              | -                |
| **0**       | Unexpected server error.                                           | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_primary_devices**

> PrimaryDevicesResponse get_primary_devices(session_id)

Get primary devices from the session protocol

Returns primary devices currently configured in the session protocol, including role name and serialized device payload. Each device object contains a \_\_type discriminator identifying the concrete CARP device type.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.primary_devices_response import PrimaryDevicesResponse
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
    api_instance = nli_engine.client._generated.authoring_client.PrimaryDevicesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.

    try:
        # Get primary devices from the session protocol
        api_response = api_instance.get_primary_devices(session_id)
        print("The response of PrimaryDevicesApi->get_primary_devices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrimaryDevicesApi->get_primary_devices: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                    | Notes |
| -------------- | ------- | ---------------------------------------------- | ----- |
| **session_id** | **str** | Session identifier returned by POST /sessions. |

### Return type

[**PrimaryDevicesResponse**](PrimaryDevicesResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description              | Response headers |
| ----------- | ------------------------ | ---------------- |
| **200**     | Primary devices returned | -                |
| **400**     | Missing session id       | -                |
| **404**     | Session id not found.    | -                |
| **0**       | Unexpected server error. | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
