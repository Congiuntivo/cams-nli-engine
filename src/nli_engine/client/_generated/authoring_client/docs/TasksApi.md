# nli_engine.client.\_generated.authoring_client.TasksApi

All URIs are relative to _http://localhost:8080_

| Method                                                     | HTTP request                                    | Description                                   |
| ---------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------- |
| [**add_app_task**](TasksApi.md#add_app_task)               | **POST** /sessions/{sessionId}/tasks/app        | Add an app task to the session protocol       |
| [**add_background_task**](TasksApi.md#add_background_task) | **POST** /sessions/{sessionId}/tasks/background | Add a background task to the session protocol |
| [**add_health_app_task**](TasksApi.md#add_health_app_task) | **POST** /sessions/{sessionId}/tasks/health-app | Add a health app task to the session protocol |
| [**add_web_task**](TasksApi.md#add_web_task)               | **POST** /sessions/{sessionId}/tasks/web        | Add a web task to the session protocol        |
| [**get_tasks**](TasksApi.md#get_tasks)                     | **GET** /sessions/{sessionId}/tasks             | Get task summaries from the session protocol  |

# **add_app_task**

> SessionMutationResponse add_app_task(session_id, app_task_request)

Add an app task to the session protocol

Adds an in-app task to the session protocol. name must be unique. type selects the kind of app task (e.g. survey). title and instructions are shown to the participant. expire sets the time window (as a DurationRequest) within which the task must be completed. measures is optional; "dk.cachet.carp.health" may be included using samplingType "health" to collect health data alongside the task.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.app_task_request import AppTaskRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TasksApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    app_task_request = {"name":"daily_survey_app_task","description":"Run a survey task in the app.","type":"survey","title":"Daily Survey","instructions":"Answer the questionnaire in-app.","minutesToComplete":5,"expire":{"hours":2},"notification":true,"measures":[{"measureType":"dk.cachet.carp.activity"}]} # AppTaskRequest | App task payload.

    try:
        # Add an app task to the session protocol
        api_response = api_instance.add_app_task(session_id, app_task_request)
        print("The response of TasksApi->add_app_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->add_app_task: %s\n" % e)
```

### Parameters

| Name                 | Type                                    | Description                                    | Notes |
| -------------------- | --------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**       | **str**                                 | Session identifier returned by POST /sessions. |
| **app_task_request** | [**AppTaskRequest**](AppTaskRequest.md) | App task payload.                              |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                                         | Response headers |
| ----------- | ----------------------------------------------------------------------------------- | ---------------- |
| **201**     | App task added                                                                      | -                |
| **400**     | Invalid request payload, unsupported app task type, or unsupported measure/sampling | -                |
| **404**     | Session id not found.                                                               | -                |
| **0**       | Unexpected server error.                                                            | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_background_task**

> SessionMutationResponse add_background_task(session_id, background_task_request)

Add a background task to the session protocol

Adds a background sensing task to the session protocol. name must be unique within the protocol. measures is a list of objects each with a measureType (CARP measure type URI) and an optional samplingConfiguration. To collect health data from Apple Health or Google Health Connect, use measureType "dk.cachet.carp.health" with samplingType "health" and a non-empty healthDataTypes array. Returns 400 if a measure type is unrecognized or its sampling configuration is incompatible.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.background_task_request import BackgroundTaskRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TasksApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    background_task_request = {"name":"daily_context_collection","description":"Collect context snapshots during the day.","duration":{"minutes":30},"measures":[{"measureType":"dk.cachet.carp.activity"},{"measureType":"dk.cachet.carp.ambientlight","samplingConfiguration":{"samplingType":"periodic","interval":{"minutes":5},"duration":{"seconds":10}}},{"measureType":"dk.cachet.carp.health","samplingConfiguration":{"samplingType":"health","healthDataTypes":["STEPS","HEART_RATE"],"days":30}}]} # BackgroundTaskRequest | Background task payload.

    try:
        # Add a background task to the session protocol
        api_response = api_instance.add_background_task(session_id, background_task_request)
        print("The response of TasksApi->add_background_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->add_background_task: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                                    | Notes |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**              | **str**                                               | Session identifier returned by POST /sessions. |
| **background_task_request** | [**BackgroundTaskRequest**](BackgroundTaskRequest.md) | Background task payload.                       |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                             | Response headers |
| ----------- | ------------------------------------------------------- | ---------------- |
| **201**     | Background task added                                   | -                |
| **400**     | Invalid request payload or unsupported measure/sampling | -                |
| **404**     | Session id not found.                                   | -                |
| **0**       | Unexpected server error.                                | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_health_app_task**

> SessionMutationResponse add_health_app_task(session_id, health_app_task_request)

Add a health app task to the session protocol

Adds a health app task to the session protocol. name must be unique. types specifies which health metrics to collect via the platform health framework (Apple Health / Google Health Connect); these are surfaced to the user when they interact with the task. measures is for additional sensors to collect alongside the task (e.g. activity, ambient light). Including "dk.cachet.carp.health" in measures is allowed but unusual, since types already handles health data collection for this task type. title and instructions are shown to the participant. expire sets the task completion window as a DurationRequest.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.health_app_task_request import HealthAppTaskRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TasksApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    health_app_task_request = {"name":"daily_health_assessment","description":"Collect daily health assessment in-app.","title":"Health Assessment","instructions":"Follow the health assessment steps.","minutesToComplete":5,"expire":{"hours":1},"notification":true,"types":["STEPS"],"measures":[{"measureType":"dk.cachet.carp.activity"}]} # HealthAppTaskRequest | Health app task payload.

    try:
        # Add a health app task to the session protocol
        api_response = api_instance.add_health_app_task(session_id, health_app_task_request)
        print("The response of TasksApi->add_health_app_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->add_health_app_task: %s\n" % e)
```

### Parameters

| Name                        | Type                                                | Description                                    | Notes |
| --------------------------- | --------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**              | **str**                                             | Session identifier returned by POST /sessions. |
| **health_app_task_request** | [**HealthAppTaskRequest**](HealthAppTaskRequest.md) | Health app task payload.                       |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                                            | Response headers |
| ----------- | -------------------------------------------------------------------------------------- | ---------------- |
| **201**     | Health app task added                                                                  | -                |
| **400**     | Invalid request payload, unsupported health data type, or unsupported measure/sampling | -                |
| **404**     | Session id not found.                                                                  | -                |
| **0**       | Unexpected server error.                                                               | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_web_task**

> SessionMutationResponse add_web_task(session_id, web_task_request)

Add a web task to the session protocol

Adds a web-based task to the session protocol. name must be unique. url specifies the web page or survey the participant will be directed to. title and description are shown to the participant in the app. measures is optional.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.models.web_task_request import WebTaskRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TasksApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    web_task_request = {"name":"daily_survey","description":"Open a daily web survey for participants.","url":"https://example.org/surveys/daily","measures":[{"measureType":"dk.cachet.carp.activity"}]} # WebTaskRequest | Web task payload.

    try:
        # Add a web task to the session protocol
        api_response = api_instance.add_web_task(session_id, web_task_request)
        print("The response of TasksApi->add_web_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->add_web_task: %s\n" % e)
```

### Parameters

| Name                 | Type                                    | Description                                    | Notes |
| -------------------- | --------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**       | **str**                                 | Session identifier returned by POST /sessions. |
| **web_task_request** | [**WebTaskRequest**](WebTaskRequest.md) | Web task payload.                              |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                           | Response headers |
| ----------- | --------------------------------------------------------------------- | ---------------- |
| **201**     | Web task added                                                        | -                |
| **400**     | Invalid request payload, invalid URL, or unsupported measure/sampling | -                |
| **404**     | Session id not found.                                                 | -                |
| **0**       | Unexpected server error.                                              | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_tasks**

> TasksResponse get_tasks(session_id)

Get task summaries from the session protocol

Returns task summaries currently configured in the session protocol. Each summary includes the full serialized task object, which contains a \_\_type discriminator identifying the concrete CARP task type.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.tasks_response import TasksResponse
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
    api_instance = nli_engine.client._generated.authoring_client.TasksApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.

    try:
        # Get task summaries from the session protocol
        api_response = api_instance.get_tasks(session_id)
        print("The response of TasksApi->get_tasks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->get_tasks: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                    | Notes |
| -------------- | ------- | ---------------------------------------------- | ----- |
| **session_id** | **str** | Session identifier returned by POST /sessions. |

### Return type

[**TasksResponse**](TasksResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description              | Response headers |
| ----------- | ------------------------ | ---------------- |
| **200**     | Task summaries returned  | -                |
| **400**     | Missing session id       | -                |
| **404**     | Session id not found.    | -                |
| **0**       | Unexpected server error. | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
