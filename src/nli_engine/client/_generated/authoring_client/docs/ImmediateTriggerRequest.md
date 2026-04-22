# ImmediateTriggerRequest

## Properties

| Name             | Type    | Description | Notes |
| ---------------- | ------- | ----------- | ----- |
| **trigger_name** | **str** |             |

## Example

```python
from authoring_client.models.immediate_trigger_request import ImmediateTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ImmediateTriggerRequest from a JSON string
immediate_trigger_request_instance = ImmediateTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(ImmediateTriggerRequest.to_json())

# convert the object into a dict
immediate_trigger_request_dict = immediate_trigger_request_instance.to_dict()
# create an instance of ImmediateTriggerRequest from a dict
immediate_trigger_request_from_dict = ImmediateTriggerRequest.from_dict(immediate_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
