# nli_engine.client.\_generated.authoring_client.ParticipantRolesApi

All URIs are relative to _http://localhost:8080_

| Method                                                                    | HTTP request                                     | Description                                           |
| ------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| [**add_participant_role**](ParticipantRolesApi.md#add_participant_role)   | **POST** /sessions/{sessionId}/participant-roles | Add a participant role to the protocol in the session |
| [**get_participant_roles**](ParticipantRolesApi.md#get_participant_roles) | **GET** /sessions/{sessionId}/participant-roles  | Get participant role names from the session protocol  |

# **add_participant_role**

> DataEndpointResponse add_participant_role(session_id, add_participant_role_request)

Add a participant role to the protocol in the session

Adds a participant role. Protocol must already be started with POST /protocol/new.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.add_participant_role_request import AddParticipantRoleRequest
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
    api_instance = nli_engine.client._generated.authoring_client.ParticipantRolesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    add_participant_role_request = {"roleName":"Patient","isOptional":false} # AddParticipantRoleRequest | Participant role configuration payload.

    try:
        # Add a participant role to the protocol in the session
        api_response = api_instance.add_participant_role(session_id, add_participant_role_request)
        print("The response of ParticipantRolesApi->add_participant_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ParticipantRolesApi->add_participant_role: %s\n" % e)
```

### Parameters

| Name                             | Type                                                          | Description                                | Notes |
| -------------------------------- | ------------------------------------------------------------- | ------------------------------------------ | ----- |
| **session_id**                   | **str**                                                       | Session id returned by POST /protocol/new. |
| **add_participant_role_request** | [**AddParticipantRoleRequest**](AddParticipantRoleRequest.md) | Participant role configuration payload.    |

### Return type

[**DataEndpointResponse**](DataEndpointResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                     | Response headers |
| ----------- | ------------------------------- | ---------------- |
| **200**     | Participant role added          | -                |
| **400**     | Missing or invalid request body | -                |
| **404**     | Session id not found            | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_participant_roles**

> ParticipantRolesResponse get_participant_roles(session_id)

Get participant role names from the session protocol

Returns participant role names currently configured in the session protocol.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.participant_roles_response import ParticipantRolesResponse
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
    api_instance = nli_engine.client._generated.authoring_client.ParticipantRolesApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.

    try:
        # Get participant role names from the session protocol
        api_response = api_instance.get_participant_roles(session_id)
        print("The response of ParticipantRolesApi->get_participant_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ParticipantRolesApi->get_participant_roles: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                | Notes |
| -------------- | ------- | ------------------------------------------ | ----- |
| **session_id** | **str** | Session id returned by POST /protocol/new. |

### Return type

[**ParticipantRolesResponse**](ParticipantRolesResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                                | Response headers |
| ----------- | ------------------------------------------ | ---------------- |
| **200**     | Participant role names returned            | -                |
| **400**     | Missing session id or protocol not started | -                |
| **404**     | Session id not found                       | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
