# NoOpTriggerRequest

## Properties

| Name             | Type    | Description | Notes |
| ---------------- | ------- | ----------- | ----- |
| **trigger_name** | **str** |             |

## Example

```python
from authoring_client.models.no_op_trigger_request import NoOpTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NoOpTriggerRequest from a JSON string
no_op_trigger_request_instance = NoOpTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(NoOpTriggerRequest.to_json())

# convert the object into a dict
no_op_trigger_request_dict = no_op_trigger_request_instance.to_dict()
# create an instance of NoOpTriggerRequest from a dict
no_op_trigger_request_from_dict = NoOpTriggerRequest.from_dict(no_op_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
