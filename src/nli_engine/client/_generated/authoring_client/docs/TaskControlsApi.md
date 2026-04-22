# authoring_client.TaskControlsApi

All URIs are relative to _http://localhost:8080_

| Method                                                        | HTTP request                                 | Description                                 |
| ------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------- |
| [**add_task_control**](TaskControlsApi.md#add_task_control)   | **POST** /sessions/{sessionId}/task-controls | Add a task control to the session protocol  |
| [**get_task_controls**](TaskControlsApi.md#get_task_controls) | **GET** /sessions/{sessionId}/task-controls  | Get task controls from the session protocol |

# **add_task_control**

> SessionMutationResponse add_task_control(session_id, task_control_request)

Add a task control to the session protocol

Adds a task control that binds a trigger, task, and destination device role in the session protocol.

### Example

```python
import authoring_client
from authoring_client.models.session_mutation_response import SessionMutationResponse
from authoring_client.models.task_control_request import TaskControlRequest
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
    api_instance = authoring_client.TaskControlsApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    task_control_request = {"taskName":"daily_survey","triggerName":"start_now","deviceRoleName":"User Phone"} # TaskControlRequest | Task control payload.

    try:
        # Add a task control to the session protocol
        api_response = api_instance.add_task_control(session_id, task_control_request)
        print("The response of TaskControlsApi->add_task_control:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskControlsApi->add_task_control: %s\n" % e)
```

### Parameters

| Name                     | Type                                            | Description                                | Notes |
| ------------------------ | ----------------------------------------------- | ------------------------------------------ | ----- |
| **session_id**           | **str**                                         | Session id returned by POST /protocol/new. |
| **task_control_request** | [**TaskControlRequest**](TaskControlRequest.md) | Task control payload.                      |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                               | Response headers |
| ----------- | ------------------------------------------------------------------------- | ---------------- |
| **200**     | Task control added                                                        | -                |
| **400**     | Invalid request payload or unresolved task/trigger/device role references | -                |
| **404**     | Session id not found                                                      | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_task_controls**

> TaskControlsResponse get_task_controls(session_id)

Get task controls from the session protocol

Returns configured task controls currently in the session protocol, including taskControl, trigger, task, and targetDevice payloads for each entry.

### Example

```python
import authoring_client
from authoring_client.models.task_controls_response import TaskControlsResponse
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
    api_instance = authoring_client.TaskControlsApi(api_client)
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.

    try:
        # Get task controls from the session protocol
        api_response = api_instance.get_task_controls(session_id)
        print("The response of TaskControlsApi->get_task_controls:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskControlsApi->get_task_controls: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                | Notes |
| -------------- | ------- | ------------------------------------------ | ----- |
| **session_id** | **str** | Session id returned by POST /protocol/new. |

### Return type

[**TaskControlsResponse**](TaskControlsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                            | Response headers |
| ----------- | -------------------------------------- | ---------------- |
| **200**     | Expanded task control entries returned | -                |
| **400**     | Missing session id                     | -                |
| **404**     | Session id not found                   | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
