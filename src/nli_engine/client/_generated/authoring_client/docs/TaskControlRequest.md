# TaskControlRequest

## Properties

| Name                 | Type    | Description | Notes |
| -------------------- | ------- | ----------- | ----- |
| **task_name**        | **str** |             |
| **trigger_name**     | **str** |             |
| **device_role_name** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.task_control_request import TaskControlRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TaskControlRequest from a JSON string
task_control_request_instance = TaskControlRequest.from_json(json)
# print the JSON string representation of the object
print(TaskControlRequest.to_json())

# convert the object into a dict
task_control_request_dict = task_control_request_instance.to_dict()
# create an instance of TaskControlRequest from a dict
task_control_request_from_dict = TaskControlRequest.from_dict(task_control_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
