# nli_engine.client.\_generated.authoring_client.TriggersApi

All URIs are relative to _http://localhost:8080_

| Method                                                                                | HTTP request                                                | Description                                               |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------- |
| [**add_cron_scheduled_trigger**](TriggersApi.md#add_cron_scheduled_trigger)           | **POST** /sessions/{sessionId}/triggers/cron                | Add a cron scheduled trigger to the session protocol      |
| [**add_date_time_trigger**](TriggersApi.md#add_date_time_trigger)                     | **POST** /sessions/{sessionId}/triggers/date-time           | Add a date-time trigger to the session protocol           |
| [**add_delayed_trigger**](TriggersApi.md#add_delayed_trigger)                         | **POST** /sessions/{sessionId}/triggers/delayed             | Add a delayed trigger to the session protocol             |
| [**add_elapsed_time_trigger**](TriggersApi.md#add_elapsed_time_trigger)               | **POST** /sessions/{sessionId}/triggers/elapsed-time        | Add an elapsed-time trigger to the session protocol       |
| [**add_immediate_trigger**](TriggersApi.md#add_immediate_trigger)                     | **POST** /sessions/{sessionId}/triggers/immediate           | Add an immediate trigger to the session protocol          |
| [**add_manual_trigger**](TriggersApi.md#add_manual_trigger)                           | **POST** /sessions/{sessionId}/triggers/manual              | Add a manual trigger to the session protocol              |
| [**add_no_op_trigger**](TriggersApi.md#add_no_op_trigger)                             | **POST** /sessions/{sessionId}/triggers/no-op               | Add a no-op trigger to the session protocol               |
| [**add_no_user_task_trigger**](TriggersApi.md#add_no_user_task_trigger)               | **POST** /sessions/{sessionId}/triggers/no-user-task        | Add a no-user-task trigger to the session protocol        |
| [**add_one_time_trigger**](TriggersApi.md#add_one_time_trigger)                       | **POST** /sessions/{sessionId}/triggers/one-time            | Add a one-time trigger to the session protocol            |
| [**add_passive_trigger**](TriggersApi.md#add_passive_trigger)                         | **POST** /sessions/{sessionId}/triggers/passive             | Add a passive trigger to the session protocol             |
| [**add_periodic_trigger**](TriggersApi.md#add_periodic_trigger)                       | **POST** /sessions/{sessionId}/triggers/periodic            | Add a periodic trigger to the session protocol            |
| [**add_random_recurrent_trigger**](TriggersApi.md#add_random_recurrent_trigger)       | **POST** /sessions/{sessionId}/triggers/random-recurrent    | Add a random recurrent trigger to the session protocol    |
| [**add_recurrent_scheduled_trigger**](TriggersApi.md#add_recurrent_scheduled_trigger) | **POST** /sessions/{sessionId}/triggers/recurrent-scheduled | Add a recurrent scheduled trigger to the session protocol |
| [**add_sampling_event_trigger**](TriggersApi.md#add_sampling_event_trigger)           | **POST** /sessions/{sessionId}/triggers/sampling-event      | Add a sampling-event trigger to the session protocol      |
| [**add_scheduled_trigger**](TriggersApi.md#add_scheduled_trigger)                     | **POST** /sessions/{sessionId}/triggers/scheduled           | Add a scheduled trigger to the session protocol           |
| [**add_user_task_trigger**](TriggersApi.md#add_user_task_trigger)                     | **POST** /sessions/{sessionId}/triggers/user-task           | Add a user-task trigger to the session protocol           |
| [**get_triggers**](TriggersApi.md#get_triggers)                                       | **GET** /sessions/{sessionId}/triggers                      | Get configured triggers from the session protocol         |

# **add_cron_scheduled_trigger**

> SessionMutationResponse add_cron_scheduled_trigger(session_id, cron_scheduled_trigger_request)

Add a cron scheduled trigger to the session protocol

Adds a cron-based scheduled trigger. triggerName must be unique within the protocol. The individual cron fields (minute, hour, dayOfMonth, month, dayOfWeek) are all optional; an omitted field matches all values. Returns 400 if any field is out of range or triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.cron_scheduled_trigger_request import CronScheduledTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    cron_scheduled_trigger_request = {"triggerName":"daily_evening_prompt","minute":30,"hour":19} # CronScheduledTriggerRequest | Cron scheduled trigger payload.

    try:
        # Add a cron scheduled trigger to the session protocol
        api_response = api_instance.add_cron_scheduled_trigger(session_id, cron_scheduled_trigger_request)
        print("The response of TriggersApi->add_cron_scheduled_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_cron_scheduled_trigger: %s\n" % e)
```

### Parameters

| Name                               | Type                                                              | Description                                    | Notes |
| ---------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                     | **str**                                                           | Session identifier returned by POST /sessions. |
| **cron_scheduled_trigger_request** | [**CronScheduledTriggerRequest**](CronScheduledTriggerRequest.md) | Cron scheduled trigger payload.                |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                                | Response headers |
| ----------- | ---------------------------------------------------------- | ---------------- |
| **201**     | Cron scheduled trigger added                               | -                |
| **400**     | Invalid request payload, cron field range, or trigger name | -                |
| **404**     | Session id not found.                                      | -                |
| **0**       | Unexpected server error.                                   | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_date_time_trigger**

> SessionMutationResponse add_date_time_trigger(session_id, date_time_trigger_request)

Add a date-time trigger to the session protocol

Adds a trigger that fires once at the specified date and time. triggerName must be unique within the protocol. schedule must be a valid ISO 8601 date-time string. Returns 400 if the format is invalid or triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.date_time_trigger_request import DateTimeTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    date_time_trigger_request = {"triggerName":"enrollment_follow_up","schedule":"2026-10-01T09:30:00Z"} # DateTimeTriggerRequest | Date-time trigger payload.

    try:
        # Add a date-time trigger to the session protocol
        api_response = api_instance.add_date_time_trigger(session_id, date_time_trigger_request)
        print("The response of TriggersApi->add_date_time_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_date_time_trigger: %s\n" % e)
```

### Parameters

| Name                          | Type                                                    | Description                                    | Notes |
| ----------------------------- | ------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                | **str**                                                 | Session identifier returned by POST /sessions. |
| **date_time_trigger_request** | [**DateTimeTriggerRequest**](DateTimeTriggerRequest.md) | Date-time trigger payload.                     |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Date-time trigger added                           | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_delayed_trigger**

> SessionMutationResponse add_delayed_trigger(session_id, delayed_trigger_request)

Add a delayed trigger to the session protocol

Adds a trigger that fires after a fixed delay from when sensing starts. triggerName must be unique within the protocol. delay is specified as a DurationRequest object with optional days, hours, minutes, seconds, milliseconds, and microseconds fields. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.delayed_trigger_request import DelayedTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    delayed_trigger_request = {"triggerName":"delayed_prompt","delay":{"minutes":15}} # DelayedTriggerRequest | Delayed trigger payload.

    try:
        # Add a delayed trigger to the session protocol
        api_response = api_instance.add_delayed_trigger(session_id, delayed_trigger_request)
        print("The response of TriggersApi->add_delayed_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_delayed_trigger: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                                    | Notes |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**              | **str**                                               | Session identifier returned by POST /sessions. |
| **delayed_trigger_request** | [**DelayedTriggerRequest**](DelayedTriggerRequest.md) | Delayed trigger payload.                       |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Delayed trigger added                             | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_elapsed_time_trigger**

> SessionMutationResponse add_elapsed_time_trigger(session_id, elapsed_time_trigger_request)

Add an elapsed-time trigger to the session protocol

Adds a trigger that fires when elapsed time from sensing start reaches the specified duration. triggerName must be unique within the protocol. elapsedTime is specified as a DurationRequest object. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.elapsed_time_trigger_request import ElapsedTimeTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    elapsed_time_trigger_request = {"triggerName":"elapsed_30_minutes","elapsedTime":{"minutes":30}} # ElapsedTimeTriggerRequest | Elapsed-time trigger payload.

    try:
        # Add an elapsed-time trigger to the session protocol
        api_response = api_instance.add_elapsed_time_trigger(session_id, elapsed_time_trigger_request)
        print("The response of TriggersApi->add_elapsed_time_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_elapsed_time_trigger: %s\n" % e)
```

### Parameters

| Name                             | Type                                                          | Description                                    | Notes |
| -------------------------------- | ------------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                   | **str**                                                       | Session identifier returned by POST /sessions. |
| **elapsed_time_trigger_request** | [**ElapsedTimeTriggerRequest**](ElapsedTimeTriggerRequest.md) | Elapsed-time trigger payload.                  |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Elapsed-time trigger added                        | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_immediate_trigger**

> SessionMutationResponse add_immediate_trigger(session_id, immediate_trigger_request)

Add an immediate trigger to the session protocol

Adds a trigger that fires immediately when sensing starts. triggerName must be unique within the protocol. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.immediate_trigger_request import ImmediateTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    immediate_trigger_request = {"triggerName":"start_now"} # ImmediateTriggerRequest | Immediate trigger payload.

    try:
        # Add an immediate trigger to the session protocol
        api_response = api_instance.add_immediate_trigger(session_id, immediate_trigger_request)
        print("The response of TriggersApi->add_immediate_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_immediate_trigger: %s\n" % e)
```

### Parameters

| Name                          | Type                                                      | Description                                    | Notes |
| ----------------------------- | --------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                | **str**                                                   | Session identifier returned by POST /sessions. |
| **immediate_trigger_request** | [**ImmediateTriggerRequest**](ImmediateTriggerRequest.md) | Immediate trigger payload.                     |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Immediate trigger added                           | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_manual_trigger**

> SessionMutationResponse add_manual_trigger(session_id, manual_trigger_request)

Add a manual trigger to the session protocol

Adds a trigger that is fired manually by the participant or researcher. triggerName must be unique within the protocol. label and description are shown to the participant in the app. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.manual_trigger_request import ManualTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    manual_trigger_request = {"triggerName":"manual_daily_prompt","label":"Daily prompt","description":"Shown manually by the participant."} # ManualTriggerRequest | Manual trigger payload.

    try:
        # Add a manual trigger to the session protocol
        api_response = api_instance.add_manual_trigger(session_id, manual_trigger_request)
        print("The response of TriggersApi->add_manual_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_manual_trigger: %s\n" % e)
```

### Parameters

| Name                       | Type                                                | Description                                    | Notes |
| -------------------------- | --------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**             | **str**                                             | Session identifier returned by POST /sessions. |
| **manual_trigger_request** | [**ManualTriggerRequest**](ManualTriggerRequest.md) | Manual trigger payload.                        |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Manual trigger added                              | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_no_op_trigger**

> SessionMutationResponse add_no_op_trigger(session_id, no_op_trigger_request)

Add a no-op trigger to the session protocol

Adds a no-op trigger that starts immediately and never stops. Used to model tasks that run continuously from the moment sensing starts. triggerName must be unique within the protocol. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.no_op_trigger_request import NoOpTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    no_op_trigger_request = {"triggerName":"always_on"} # NoOpTriggerRequest | No-op trigger payload.

    try:
        # Add a no-op trigger to the session protocol
        api_response = api_instance.add_no_op_trigger(session_id, no_op_trigger_request)
        print("The response of TriggersApi->add_no_op_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_no_op_trigger: %s\n" % e)
```

### Parameters

| Name                      | Type                                            | Description                                    | Notes |
| ------------------------- | ----------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**            | **str**                                         | Session identifier returned by POST /sessions. |
| **no_op_trigger_request** | [**NoOpTriggerRequest**](NoOpTriggerRequest.md) | No-op trigger payload.                         |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | No-op trigger added                               | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_no_user_task_trigger**

> SessionMutationResponse add_no_user_task_trigger(session_id, no_user_task_trigger_request)

Add a no-user-task trigger to the session protocol

Adds a trigger that fires when the specified user task is absent from the task list. triggerName must be unique within the protocol. taskName references the task that must be absent. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.no_user_task_trigger_request import NoUserTaskTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    no_user_task_trigger_request = {"triggerName":"ensure_survey_task","taskName":"daily_survey"} # NoUserTaskTriggerRequest | No-user-task trigger payload.

    try:
        # Add a no-user-task trigger to the session protocol
        api_response = api_instance.add_no_user_task_trigger(session_id, no_user_task_trigger_request)
        print("The response of TriggersApi->add_no_user_task_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_no_user_task_trigger: %s\n" % e)
```

### Parameters

| Name                             | Type                                                        | Description                                    | Notes |
| -------------------------------- | ----------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                   | **str**                                                     | Session identifier returned by POST /sessions. |
| **no_user_task_trigger_request** | [**NoUserTaskTriggerRequest**](NoUserTaskTriggerRequest.md) | No-user-task trigger payload.                  |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | No-user-task trigger added                        | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_one_time_trigger**

> SessionMutationResponse add_one_time_trigger(session_id, one_time_trigger_request)

Add a one-time trigger to the session protocol

Adds a trigger that fires exactly once during the entire study deployment. triggerName must be unique within the protocol. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.one_time_trigger_request import OneTimeTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    one_time_trigger_request = {"triggerName":"show_demographics_once"} # OneTimeTriggerRequest | One-time trigger payload.

    try:
        # Add a one-time trigger to the session protocol
        api_response = api_instance.add_one_time_trigger(session_id, one_time_trigger_request)
        print("The response of TriggersApi->add_one_time_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_one_time_trigger: %s\n" % e)
```

### Parameters

| Name                         | Type                                                  | Description                                    | Notes |
| ---------------------------- | ----------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**               | **str**                                               | Session identifier returned by POST /sessions. |
| **one_time_trigger_request** | [**OneTimeTriggerRequest**](OneTimeTriggerRequest.md) | One-time trigger payload.                      |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | One-time trigger added                            | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_passive_trigger**

> SessionMutationResponse add_passive_trigger(session_id, passive_trigger_request)

Add a passive trigger to the session protocol

Adds a passive trigger that fires only when explicitly triggered from application code — no automatic scheduling. triggerName must be unique within the protocol. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.passive_trigger_request import PassiveTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    passive_trigger_request = {"triggerName":"manual_code_trigger"} # PassiveTriggerRequest | Passive trigger payload.

    try:
        # Add a passive trigger to the session protocol
        api_response = api_instance.add_passive_trigger(session_id, passive_trigger_request)
        print("The response of TriggersApi->add_passive_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_passive_trigger: %s\n" % e)
```

### Parameters

| Name                        | Type                                                  | Description                                    | Notes |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**              | **str**                                               | Session identifier returned by POST /sessions. |
| **passive_trigger_request** | [**PassiveTriggerRequest**](PassiveTriggerRequest.md) | Passive trigger payload.                       |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Passive trigger added                             | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_periodic_trigger**

> SessionMutationResponse add_periodic_trigger(session_id, periodic_trigger_request)

Add a periodic trigger to the session protocol

Adds a trigger that fires repeatedly at a fixed interval. triggerName must be unique within the protocol. period is specified as a DurationRequest object and must be greater than zero. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.periodic_trigger_request import PeriodicTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    periodic_trigger_request = {"triggerName":"periodic_prompt","period":{"minutes":20}} # PeriodicTriggerRequest | Periodic trigger payload.

    try:
        # Add a periodic trigger to the session protocol
        api_response = api_instance.add_periodic_trigger(session_id, periodic_trigger_request)
        print("The response of TriggersApi->add_periodic_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_periodic_trigger: %s\n" % e)
```

### Parameters

| Name                         | Type                                                    | Description                                    | Notes |
| ---------------------------- | ------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**               | **str**                                                 | Session identifier returned by POST /sessions. |
| **periodic_trigger_request** | [**PeriodicTriggerRequest**](PeriodicTriggerRequest.md) | Periodic trigger payload.                      |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Periodic trigger added                            | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_random_recurrent_trigger**

> SessionMutationResponse add_random_recurrent_trigger(session_id, random_recurrent_trigger_request)

Add a random recurrent trigger to the session protocol

Adds a trigger that fires at random times within a daily time window. triggerName must be unique within the protocol. minNumberOfTriggers and maxNumberOfTriggers bound how many times the trigger may fire each day. startTime and endTime define the daily window as clock time objects with hour and minute fields. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.random_recurrent_trigger_request import RandomRecurrentTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    random_recurrent_trigger_request = {"triggerName":"random_daily_prompts","minNumberOfTriggers":3,"maxNumberOfTriggers":8,"startTime":{"hour":8,"minute":0},"endTime":{"hour":20,"minute":0}} # RandomRecurrentTriggerRequest | Random recurrent trigger payload.

    try:
        # Add a random recurrent trigger to the session protocol
        api_response = api_instance.add_random_recurrent_trigger(session_id, random_recurrent_trigger_request)
        print("The response of TriggersApi->add_random_recurrent_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_random_recurrent_trigger: %s\n" % e)
```

### Parameters

| Name                                 | Type                                                                  | Description                                    | Notes |
| ------------------------------------ | --------------------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                       | **str**                                                               | Session identifier returned by POST /sessions. |
| **random_recurrent_trigger_request** | [**RandomRecurrentTriggerRequest**](RandomRecurrentTriggerRequest.md) | Random recurrent trigger payload.              |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Random recurrent trigger added                    | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_recurrent_scheduled_trigger**

> SessionMutationResponse add_recurrent_scheduled_trigger(session_id, recurrent_scheduled_trigger_request)

Add a recurrent scheduled trigger to the session protocol

Adds a trigger that fires at a fixed clock time on a recurring schedule. triggerName must be unique within the protocol. type selects the recurrence (daily, weekly, monthly). For weekly recurrence dayOfWeek is required (1=Monday); for monthly recurrence dayOfMonth is required. time specifies the clock time with hour and minute fields. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.recurrent_scheduled_trigger_request import RecurrentScheduledTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    recurrent_scheduled_trigger_request = {"triggerName":"weekday_checkin","type":"weekly","time":{"hour":9,"minute":30},"dayOfWeek":1} # RecurrentScheduledTriggerRequest | Recurrent scheduled trigger payload.

    try:
        # Add a recurrent scheduled trigger to the session protocol
        api_response = api_instance.add_recurrent_scheduled_trigger(session_id, recurrent_scheduled_trigger_request)
        print("The response of TriggersApi->add_recurrent_scheduled_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_recurrent_scheduled_trigger: %s\n" % e)
```

### Parameters

| Name                                    | Type                                                                        | Description                                    | Notes |
| --------------------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                          | **str**                                                                     | Session identifier returned by POST /sessions. |
| **recurrent_scheduled_trigger_request** | [**RecurrentScheduledTriggerRequest**](RecurrentScheduledTriggerRequest.md) | Recurrent scheduled trigger payload.           |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Recurrent scheduled trigger added                 | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_sampling_event_trigger**

> SessionMutationResponse add_sampling_event_trigger(session_id, sampling_event_trigger_request)

Add a sampling-event trigger to the session protocol

Adds a trigger that fires when data of a specific measure type is sampled and optionally matches a condition. triggerName must be unique within the protocol. measureType is the CARP data type URI whose measurements are evaluated. triggerCondition is an optional serialized CARP Data object (including \_\_type); when provided, only measurements matching its fields fire the trigger. Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.sampling_event_trigger_request import SamplingEventTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    sampling_event_trigger_request = {"triggerName":"after_completed_task","measureType":"dk.cachet.carp.completed_task","triggerCondition":{"__type":"dk.cachet.carp.common.application.data.completedtask"}} # SamplingEventTriggerRequest | Sampling-event trigger payload. triggerCondition is optional and should follow serialized CARP Data format.

    try:
        # Add a sampling-event trigger to the session protocol
        api_response = api_instance.add_sampling_event_trigger(session_id, sampling_event_trigger_request)
        print("The response of TriggersApi->add_sampling_event_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_sampling_event_trigger: %s\n" % e)
```

### Parameters

| Name                               | Type                                                              | Description                                                                                                 | Notes |
| ---------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----- |
| **session_id**                     | **str**                                                           | Session identifier returned by POST /sessions.                                                              |
| **sampling_event_trigger_request** | [**SamplingEventTriggerRequest**](SamplingEventTriggerRequest.md) | Sampling-event trigger payload. triggerCondition is optional and should follow serialized CARP Data format. |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Sampling-event trigger added                      | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_scheduled_trigger**

> SessionMutationResponse add_scheduled_trigger(session_id, scheduled_trigger_request)

Add a scheduled trigger to the session protocol

Adds a trigger with a time and a full recurrence rule based on RFC 5545 concepts. triggerName must be unique within the protocol. time specifies the clock time (hour, minute, optional second). recurrenceRule selects the frequency (daily, weekly, monthly, yearly), the interval, and the end condition (never, count, or elapsed time). Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.scheduled_trigger_request import ScheduledTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    scheduled_trigger_request = {"triggerName":"daily_checkin","time":{"hour":9,"minute":0},"recurrenceRule":{"frequency":"daily","interval":1,"end":{"type":"never"}}} # ScheduledTriggerRequest | Scheduled trigger payload.

    try:
        # Add a scheduled trigger to the session protocol
        api_response = api_instance.add_scheduled_trigger(session_id, scheduled_trigger_request)
        print("The response of TriggersApi->add_scheduled_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_scheduled_trigger: %s\n" % e)
```

### Parameters

| Name                          | Type                                                      | Description                                    | Notes |
| ----------------------------- | --------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                | **str**                                                   | Session identifier returned by POST /sessions. |
| **scheduled_trigger_request** | [**ScheduledTriggerRequest**](ScheduledTriggerRequest.md) | Scheduled trigger payload.                     |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | Scheduled trigger added                           | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_user_task_trigger**

> SessionMutationResponse add_user_task_trigger(session_id, user_task_trigger_request)

Add a user-task trigger to the session protocol

Adds a trigger that fires when a named user task reaches the specified state. triggerName must be unique within the protocol. taskName identifies the user task to watch; triggerCondition specifies the required state (e.g. done, expired, discarded). Returns 400 if triggerName is a duplicate.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse
from nli_engine.client._generated.authoring_client.models.user_task_trigger_request import UserTaskTriggerRequest
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.
    user_task_trigger_request = {"triggerName":"survey_completion_trigger","taskName":"daily_survey","triggerCondition":"done"} # UserTaskTriggerRequest | User-task trigger payload.

    try:
        # Add a user-task trigger to the session protocol
        api_response = api_instance.add_user_task_trigger(session_id, user_task_trigger_request)
        print("The response of TriggersApi->add_user_task_trigger:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->add_user_task_trigger: %s\n" % e)
```

### Parameters

| Name                          | Type                                                    | Description                                    | Notes |
| ----------------------------- | ------------------------------------------------------- | ---------------------------------------------- | ----- |
| **session_id**                | **str**                                                 | Session identifier returned by POST /sessions. |
| **user_task_trigger_request** | [**UserTaskTriggerRequest**](UserTaskTriggerRequest.md) | User-task trigger payload.                     |

### Return type

[**SessionMutationResponse**](SessionMutationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details

| Status code | Description                                       | Response headers |
| ----------- | ------------------------------------------------- | ---------------- |
| **201**     | User-task trigger added                           | -                |
| **400**     | Invalid request payload or duplicate trigger name | -                |
| **404**     | Session id not found.                             | -                |
| **0**       | Unexpected server error.                          | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_triggers**

> TriggersResponse get_triggers(session_id)

Get configured triggers from the session protocol

Returns trigger summaries currently configured in the session protocol. Each summary includes the full serialized trigger object, which contains a \_\_type discriminator identifying the concrete CARP trigger type.

### Example

```python
import nli_engine.client._generated.authoring_client
from nli_engine.client._generated.authoring_client.models.triggers_response import TriggersResponse
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
    api_instance = nli_engine.client._generated.authoring_client.TriggersApi(api_client)
    session_id = 'session_1234567890_1' # str | Session identifier returned by POST /sessions.

    try:
        # Get configured triggers from the session protocol
        api_response = api_instance.get_triggers(session_id)
        print("The response of TriggersApi->get_triggers:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->get_triggers: %s\n" % e)
```

### Parameters

| Name           | Type    | Description                                    | Notes |
| -------------- | ------- | ---------------------------------------------- | ----- |
| **session_id** | **str** | Session identifier returned by POST /sessions. |

### Return type

[**TriggersResponse**](TriggersResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description                | Response headers |
| ----------- | -------------------------- | ---------------- |
| **200**     | Trigger summaries returned | -                |
| **400**     | Missing session id         | -                |
| **404**     | Session id not found.      | -                |
| **0**       | Unexpected server error.   | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
