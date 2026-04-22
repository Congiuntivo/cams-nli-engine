# BackgroundTaskRequest

## Properties

| Name            | Type                                                  | Description | Notes      |
| --------------- | ----------------------------------------------------- | ----------- | ---------- |
| **name**        | **str**                                               |             |
| **description** | **str**                                               |             |
| **measures**    | [**List[TaskMeasureRequest]**](TaskMeasureRequest.md) |             |
| **duration**    | [**DurationRequest**](DurationRequest.md)             |             | [optional] |

## Example

```python
from authoring_client.models.background_task_request import BackgroundTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BackgroundTaskRequest from a JSON string
background_task_request_instance = BackgroundTaskRequest.from_json(json)
# print the JSON string representation of the object
print(BackgroundTaskRequest.to_json())

# convert the object into a dict
background_task_request_dict = background_task_request_instance.to_dict()
# create an instance of BackgroundTaskRequest from a dict
background_task_request_from_dict = BackgroundTaskRequest.from_dict(background_task_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
