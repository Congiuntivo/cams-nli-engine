# nli_engine.client.\_generated.authoring_client.DataEndpointApi

All URIs are relative to _http://localhost:8080_

| Method                                                        | HTTP request                                 | Description                                      |
| ------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------ |
| [**add_data_endpoint**](DataEndpointApi.md#add_data_endpoint) | **POST** /sessions/{sessionId}/data-endpoint | Add a data endpoint to a protocol in the session |

# **add_data_endpoint**

> DataEndpointResponse add_data_endpoint(session_id, data_endpoint_request)

Add a data endpoint to a protocol in the session

Adds a data endpoint to the session protocol. Protocol must already be started with POST /protocol/new.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.data_endpoint_request import DataEndpointRequest
from nli_engine.client._generated.authoring_client.models.data_endpoint_response import DataEndpointResponse
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
    api_instance = nli_engine.client._generated.authoring_client.DataEndpointApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    data_endpoint_request = {"endpointType":"CAWS","uploadMethod":"stream","name":"CARP Web Services","deleteWhenUploaded":true} # DataEndpointRequest | Data endpoint configuration payload.

    try:
        # Add a data endpoint to a protocol in the session
        api_response = api_instance.add_data_endpoint(session_id, data_endpoint_request)
        print("The response of DataEndpointApi->add_data_endpoint:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataEndpointApi->add_data_endpoint: %s\n" % e)
```

### Parameters

| Name                      | Type                                              | Description                                | Notes |
| ------------------------- | ------------------------------------------------- | ------------------------------------------ | ----- |
| **session_id**            | **str**                                           | Session id returned by POST /protocol/new. |
| **data_endpoint_request** | [**DataEndpointRequest**](DataEndpointRequest.md) | Data endpoint configuration payload.       |

### Return type

[**DataEndpointResponse**](DataEndpointResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                         | Response headers |
| ----------- | ----------------------------------- | ---------------- |
| **200**     | Data endpoint added                 | -                |
| **400**     | Missing or invalid query parameters | -                |
| **404**     | Session id not found                | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
