# AppTaskRequest

## Properties

| Name                    | Type                                                  | Description | Notes      |
| ----------------------- | ----------------------------------------------------- | ----------- | ---------- |
| **name**                | **str**                                               |             |
| **description**         | **str**                                               |             |
| **measures**            | [**List[TaskMeasureRequest]**](TaskMeasureRequest.md) |             |
| **type**                | **str**                                               |             |
| **title**               | **str**                                               |             | [optional] |
| **instructions**        | **str**                                               |             | [optional] |
| **minutes_to_complete** | **int**                                               |             | [optional] |
| **expire**              | [**DurationRequest**](DurationRequest.md)             |             | [optional] |
| **notification**        | **bool**                                              |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.app_task_request import AppTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AppTaskRequest from a JSON string
app_task_request_instance = AppTaskRequest.from_json(json)
# print the JSON string representation of the object
print(AppTaskRequest.to_json())

# convert the object into a dict
app_task_request_dict = app_task_request_instance.to_dict()
# create an instance of AppTaskRequest from a dict
app_task_request_from_dict = AppTaskRequest.from_dict(app_task_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
