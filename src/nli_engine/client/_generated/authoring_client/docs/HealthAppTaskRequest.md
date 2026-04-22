# HealthAppTaskRequest

## Properties

| Name                    | Type                                                  | Description | Notes      |
| ----------------------- | ----------------------------------------------------- | ----------- | ---------- |
| **name**                | **str**                                               |             |
| **description**         | **str**                                               |             |
| **measures**            | [**List[TaskMeasureRequest]**](TaskMeasureRequest.md) |             |
| **types**               | **List[str]**                                         |             |
| **title**               | **str**                                               |             | [optional] |
| **instructions**        | **str**                                               |             | [optional] |
| **minutes_to_complete** | **int**                                               |             | [optional] |
| **expire**              | [**DurationRequest**](DurationRequest.md)             |             | [optional] |
| **notification**        | **bool**                                              |             | [optional] |

## Example

```python
from authoring_client.models.health_app_task_request import HealthAppTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HealthAppTaskRequest from a JSON string
health_app_task_request_instance = HealthAppTaskRequest.from_json(json)
# print the JSON string representation of the object
print(HealthAppTaskRequest.to_json())

# convert the object into a dict
health_app_task_request_dict = health_app_task_request_instance.to_dict()
# create an instance of HealthAppTaskRequest from a dict
health_app_task_request_from_dict = HealthAppTaskRequest.from_dict(health_app_task_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
