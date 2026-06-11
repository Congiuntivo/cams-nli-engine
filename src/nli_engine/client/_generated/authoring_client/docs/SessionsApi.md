# nli_engine.client.\_generated.authoring_client.SessionsApi

All URIs are relative to _http://localhost:8080_

| Method                                                                | HTTP request                                   | Description                                 |
| --------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------- |
| [**create_protocol_session**](SessionsApi.md#create_protocol_session) | **POST** /sessions                             | Create a new protocol authoring session     |
| [**set_application_data**](SessionsApi.md#set_application_data)       | **PUT** /sessions/{sessionId}/application-data | Set custom application data on the protocol |

# **create_protocol_session**

> CreateSessionResponse create_protocol_session(create_protocol_request)

Create a new protocol authoring session

Creates an in-memory authoring session and returns a sessionId for all subsequent requests. Sessions are not persisted — restarting the server destroys all sessions. name is required; all other fields are optional and customize the resulting protocol metadata. The sessionId returned here must be included in the path of every subsequent call.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.create_protocol_request import CreateProtocolRequest
from nli_engine.client._generated.authoring_client.models.create_session_response import CreateSessionResponse
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
    api_instance = nli_engine.client._generated.authoring_client.SessionsApi(api_client)
    create_protocol_request = {"name":"My Study Protocol","ownerId":"979b408d-784e-4b1b-bb1e-ff9204e072f3","protocolVersionTag":"v1.0.0","applicationName":"carp_study_app","privacySchemaName":"default-privacy-schema"} # CreateProtocolRequest | Protocol creation payload.

    try:
        # Create a new protocol authoring session
        api_response = api_instance.create_protocol_session(create_protocol_request)
        print("The response of SessionsApi->create_protocol_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->create_protocol_session: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                | Notes |
| --------------------------- | ----------------------------------------------------- | -------------------------- | ----- |
| **create_protocol_request** | [**CreateProtocolRequest**](CreateProtocolRequest.md) | Protocol creation payload. |

### Return type

[**CreateSessionResponse**](CreateSessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                   | Response headers |
| ----------- | ----------------------------- | ---------------- |
| **201**     | New authoring session created | -                |
| **0**       | Unexpected server error.      | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_application_data**

> SessionMutationResponse set_application_data(session_id, set_application_data_request)

Set custom application data on the protocol

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.models.set_application_data_request import SetApplicationDataRequest
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
    api_instance = nli_engine.client._generated.authoring_client.SessionsApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    set_application_data_request = {"myKey":"myValue"} # SetApplicationDataRequest | Free-form key/value map to store as custom application data.

    try:
        # Set custom application data on the protocol
        api_response = api_instance.set_application_data(session_id, set_application_data_request)
        print("The response of SessionsApi->set_application_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->set_application_data: %s\n" % e)
```

### Parameters

| Name                             | Type                                                          | Description                                                  | Notes |
| -------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------ | ----- |
| **session_id**                   | **str**                                                       | Session identifier returned by POST /sessions.               |
| **set_application_data_request** | [**SetApplicationDataRequest**](SetApplicationDataRequest.md) | Free-form key/value map to store as custom application data. |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description              | Response headers |
| ----------- | ------------------------ | ---------------- |
| **200**     | Application data updated | -                |
| **404**     | Session id not found.    | -                |
| **0**       | Unexpected server error. | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
