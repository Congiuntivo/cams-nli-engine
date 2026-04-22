# NoUserTaskTriggerRequest

## Properties

| Name             | Type    | Description | Notes |
| ---------------- | ------- | ----------- | ----- |
| **trigger_name** | **str** |             |
| **task_name**    | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.no_user_task_trigger_request import NoUserTaskTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NoUserTaskTriggerRequest from a JSON string
no_user_task_trigger_request_instance = NoUserTaskTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(NoUserTaskTriggerRequest.to_json())

# convert the object into a dict
no_user_task_trigger_request_dict = no_user_task_trigger_request_instance.to_dict()
# create an instance of NoUserTaskTriggerRequest from a dict
no_user_task_trigger_request_from_dict = NoUserTaskTriggerRequest.from_dict(no_user_task_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
