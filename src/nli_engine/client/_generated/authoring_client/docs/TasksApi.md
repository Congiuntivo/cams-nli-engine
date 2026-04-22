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

Adds an app task with one or more measures and an app task type to the current session protocol.

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
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
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

| Name                 | Type                                    | Description                                | Notes |
| -------------------- | --------------------------------------- | ------------------------------------------ | ----- |
| **session_id**       | **str**                                 | Session id returned by POST /protocol/new. |
| **app_task_request** | [**AppTaskRequest**](AppTaskRequest.md) | App task payload.                          |

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
| **200**     | App task added                                                                      | -                |
| **400**     | Invalid request payload, unsupported app task type, or unsupported measure/sampling | -                |
| **404**     | Session id not found                                                                | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_background_task**

> SessionMutationResponse add_background_task(session_id, background_task_request)

Add a background task to the session protocol

Adds a background task with one or more measures to the current session protocol.

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
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
    background_task_request = {"name":"daily_context_collection","description":"Collect context snapshots during the day.","duration":{"minutes":30},"measures":[{"measureType":"dk.cachet.carp.activity"},{"measureType":"dk.cachet.carp.ambientlight","samplingConfiguration":{"samplingType":"periodic","interval":{"minutes":5},"duration":{"seconds":10}}}]} # BackgroundTaskRequest | Background task payload.

    try:
        # Add a background task to the session protocol
        api_response = api_instance.add_background_task(session_id, background_task_request)
        print("The response of TasksApi->add_background_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->add_background_task: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                                | Notes |
| --------------------------- | ----------------------------------------------------- | ------------------------------------------ | ----- |
| **session_id**              | **str**                                               | Session id returned by POST /protocol/new. |
| **background_task_request** | [**BackgroundTaskRequest**](BackgroundTaskRequest.md) | Background task payload.                   |

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
| **200**     | Background task added                                   | -                |
| **400**     | Invalid request payload or unsupported measure/sampling | -                |
| **404**     | Session id not found                                    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_health_app_task**

> SessionMutationResponse add_health_app_task(session_id, health_app_task_request)

Add a health app task to the session protocol

Adds a health app task with one or more measures and health data types to the current session protocol.

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
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
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

| Name                        | Type                                                | Description                                | Notes |
| --------------------------- | --------------------------------------------------- | ------------------------------------------ | ----- |
| **session_id**              | **str**                                             | Session id returned by POST /protocol/new. |
| **health_app_task_request** | [**HealthAppTaskRequest**](HealthAppTaskRequest.md) | Health app task payload.                   |

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
| **200**     | Health app task added                                                                  | -                |
| **400**     | Invalid request payload, unsupported health data type, or unsupported measure/sampling | -                |
| **404**     | Session id not found                                                                   | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_web_task**

> SessionMutationResponse add_web_task(session_id, web_task_request)

Add a web task to the session protocol

Adds a web task with one or more measures and a valid URL to the current session protocol.

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
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.
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

| Name                 | Type                                    | Description                                | Notes |
| -------------------- | --------------------------------------- | ------------------------------------------ | ----- |
| **session_id**       | **str**                                 | Session id returned by POST /protocol/new. |
| **web_task_request** | [**WebTaskRequest**](WebTaskRequest.md) | Web task payload.                          |

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
| **200**     | Web task added                                                        | -                |
| **400**     | Invalid request payload, invalid URL, or unsupported measure/sampling | -                |
| **404**     | Session id not found                                                  | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_tasks**

> TasksResponse get_tasks(session_id)

Get task summaries from the session protocol

Returns configured task names and serialized task configurations currently in the session protocol.

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
    session_id = 'session_1234567890_1' # str | Session id returned by POST /protocol/new.

    try:
        # Get task summaries from the session protocol
        api_response = api_instance.get_tasks(session_id)
        print("The response of TasksApi->get_tasks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->get_tasks: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                | Notes |
| -------------- | ------- | ------------------------------------------ | ----- |
| **session_id** | **str** | Session id returned by POST /protocol/new. |

### Return type

[**TasksResponse**](TasksResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description             | Response headers |
| ----------- | ----------------------- | ---------------- |
| **200**     | Task summaries returned | -                |
| **400**     | Missing session id      | -                |
| **404**     | Session id not found    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
