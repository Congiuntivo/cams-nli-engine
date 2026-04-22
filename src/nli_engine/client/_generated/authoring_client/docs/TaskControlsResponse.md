# TaskControlsResponse

## Properties

| Name              | Type                                                  | Description | Notes |
| ----------------- | ----------------------------------------------------- | ----------- | ----- |
| **task_controls** | [**List[TaskControlSummary]**](TaskControlSummary.md) |             |

## Example

```python
from authoring_client.models.task_controls_response import TaskControlsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TaskControlsResponse from a JSON string
task_controls_response_instance = TaskControlsResponse.from_json(json)
# print the JSON string representation of the object
print(TaskControlsResponse.to_json())

# convert the object into a dict
task_controls_response_dict = task_controls_response_instance.to_dict()
# create an instance of TaskControlsResponse from a dict
task_controls_response_from_dict = TaskControlsResponse.from_dict(task_controls_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
