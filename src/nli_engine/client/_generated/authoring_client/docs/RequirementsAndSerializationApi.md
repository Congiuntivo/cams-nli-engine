# authoring_client.RequirementsAndSerializationApi

All URIs are relative to _http://localhost:8080_

| Method                                                                          | HTTP request                               | Description                                          |
| ------------------------------------------------------------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| [**get_requirements**](RequirementsAndSerializationApi.md#get_requirements)     | **GET** /sessions/{sessionId}/requirements | Get current unfulfilled requirements for the session |
| [**serialize_protocol**](RequirementsAndSerializationApi.md#serialize_protocol) | **GET** /sessions/{sessionId}/serialize    | Return the serialized protocol for the session       |

# **get_requirements**

> RequirementsResponse get_requirements(session_id)

Get current unfulfilled requirements for the session

Returns the current unfulfilled requirements for the session.

### Example

```python
import authoring_client
from authoring_client.models.requirements_response import RequirementsResponse
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
    api_instance = authoring_client.RequirementsAndSerializationApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.

    try:
        # Get current unfulfilled requirements for the session
        api_response = api_instance.get_requirements(session_id)
        print("The response of RequirementsAndSerializationApi->get_requirements:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RequirementsAndSerializationApi->get_requirements: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                | Notes |
| -------------- | ------- | ------------------------------------------ | ----- |
| **session_id** | **str** | Session id returned by POST /protocol/new. |

### Return type

[**RequirementsResponse**](RequirementsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                                      | Response headers |
| ----------- | ------------------------------------------------ | ---------------- |
| **200**     | Current unfulfilled requirements for the session | -                |
| **400**     | Missing session id                               | -                |
| **404**     | Session id not found                             | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **serialize_protocol**

> SerializeResponse serialize_protocol(session_id)

Return the serialized protocol for the session

Returns the serialized protocol for the session.

### Example

```python
import authoring_client
from authoring_client.models.serialize_response import SerializeResponse
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
    api_instance = authoring_client.RequirementsAndSerializationApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.

    try:
        # Return the serialized protocol for the session
        api_response = api_instance.serialize_protocol(session_id)
        print("The response of RequirementsAndSerializationApi->serialize_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RequirementsAndSerializationApi->serialize_protocol: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                | Notes |
| -------------- | ------- | ------------------------------------------ | ----- |
| **session_id** | **str** | Session id returned by POST /protocol/new. |

### Return type

[**SerializeResponse**](SerializeResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                             | Response headers |
| ----------- | ----------------------------------------------------------------------- | ---------------- |
| **200**     | Serialized protocol for the session                                     | -                |
| **400**     | Missing session id                                                      | -                |
| **409**     | Protocol cannot be serialized until critical requirements are fulfilled | -                |
| **404**     | Session id not found                                                    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
