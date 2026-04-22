# UserTaskTriggerRequest

## Properties

| Name                  | Type    | Description | Notes |
| --------------------- | ------- | ----------- | ----- |
| **trigger_name**      | **str** |             |
| **task_name**         | **str** |             |
| **trigger_condition** | **str** |             |

## Example

```python
from authoring_client.models.user_task_trigger_request import UserTaskTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UserTaskTriggerRequest from a JSON string
user_task_trigger_request_instance = UserTaskTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(UserTaskTriggerRequest.to_json())

# convert the object into a dict
user_task_trigger_request_dict = user_task_trigger_request_instance.to_dict()
# create an instance of UserTaskTriggerRequest from a dict
user_task_trigger_request_from_dict = UserTaskTriggerRequest.from_dict(user_task_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
