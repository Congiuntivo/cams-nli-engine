# PassiveTriggerRequest

## Properties

| Name             | Type    | Description | Notes |
| ---------------- | ------- | ----------- | ----- |
| **trigger_name** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.passive_trigger_request import PassiveTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PassiveTriggerRequest from a JSON string
passive_trigger_request_instance = PassiveTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(PassiveTriggerRequest.to_json())

# convert the object into a dict
passive_trigger_request_dict = passive_trigger_request_instance.to_dict()
# create an instance of PassiveTriggerRequest from a dict
passive_trigger_request_from_dict = PassiveTriggerRequest.from_dict(passive_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
