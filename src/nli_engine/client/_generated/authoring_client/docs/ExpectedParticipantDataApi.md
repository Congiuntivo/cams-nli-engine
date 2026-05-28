# nli_engine.client.\_generated.authoring_client.ExpectedParticipantDataApi

All URIs are relative to _http://localhost:8080_

| Method                                                                                                                       | HTTP request                                                   | Description                                       |
| ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| [**add_expected_participant_data_for_all_roles**](ExpectedParticipantDataApi.md#add_expected_participant_data_for_all_roles) | **POST** /sessions/{sessionId}/expected-data                   | Add expected participant data for all roles       |
| [**add_expected_participant_data_for_role**](ExpectedParticipantDataApi.md#add_expected_participant_data_for_role)           | **POST** /sessions/{sessionId}/participant-roles/expected-data | Add expected participant data for a specific role |

# **add_expected_participant_data_for_all_roles**

> SessionMutationResponse add_expected_participant_data_for_all_roles(session_id, add_expected_participant_data_request)

Add expected participant data for all roles

Declares that all participant roles are expected to provide the given dataType. dataType must be one of the enum values listed in ParticipantDataType.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.add_expected_participant_data_request import AddExpectedParticipantDataRequest
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
    api_instance = nli_engine.client._generated.authoring_client.ExpectedParticipantDataApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    add_expected_participant_data_request = {"dataType":"informed_consent"} # AddExpectedParticipantDataRequest | Expected participant data type payload.

    try:
        # Add expected participant data for all roles
        api_response = api_instance.add_expected_participant_data_for_all_roles(session_id, add_expected_participant_data_request)
        print("The response of ExpectedParticipantDataApi->add_expected_participant_data_for_all_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpectedParticipantDataApi->add_expected_participant_data_for_all_roles: %s\n" % e)
```

### Parameters

| Name                                      | Type                                                                          | Description                                    | Notes |
| ----------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                            | **str**                                                                       | Session identifier returned by POST /sessions. |
| **add_expected_participant_data_request** | [**AddExpectedParticipantDataRequest**](AddExpectedParticipantDataRequest.md) | Expected participant data type payload.        |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                   | Response headers |
| ----------- | --------------------------------------------- | ---------------- |
| **201**     | Expected participant data added for all roles | -                |
| **400**     | Missing or invalid request body               | -                |
| **404**     | Session id not found.                         | -                |
| **0**       | Unexpected server error.                      | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_expected_participant_data_for_role**

> SessionMutationResponse add_expected_participant_data_for_role(session_id, add_expected_participant_data_for_role_request)

Add expected participant data for a specific role

Declares that a specific participant role is expected to provide the given dataType. roleName must match an existing participant role; if it does not, the session carries an unfulfilled requirement. dataType must be one of the enum values listed in ParticipantDataType.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.add_expected_participant_data_for_role_request import AddExpectedParticipantDataForRoleRequest
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
    api_instance = nli_engine.client._generated.authoring_client.ExpectedParticipantDataApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    add_expected_participant_data_for_role_request = {"roleName":"Patient","dataType":"sex"} # AddExpectedParticipantDataForRoleRequest | Expected participant data payload for a specific role.

    try:
        # Add expected participant data for a specific role
        api_response = api_instance.add_expected_participant_data_for_role(session_id, add_expected_participant_data_for_role_request)
        print("The response of ExpectedParticipantDataApi->add_expected_participant_data_for_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpectedParticipantDataApi->add_expected_participant_data_for_role: %s\n" % e)
```

### Parameters

| Name                                               | Type                                                                                        | Description                                            | Notes |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ----- |
| **session_id**                                     | **str**                                                                                     | Session identifier returned by POST /sessions.         |
| **add_expected_participant_data_for_role_request** | [**AddExpectedParticipantDataForRoleRequest**](AddExpectedParticipantDataForRoleRequest.md) | Expected participant data payload for a specific role. |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                              | Response headers |
| ----------- | ---------------------------------------- | ---------------- |
| **201**     | Expected participant data added for role | -                |
| **400**     | Missing or invalid request body          | -                |
| **404**     | Session id not found.                    | -                |
| **0**       | Unexpected server error.                 | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
