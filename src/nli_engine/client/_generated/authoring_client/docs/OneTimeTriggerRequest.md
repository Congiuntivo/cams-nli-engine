# OneTimeTriggerRequest

## Properties

| Name             | Type    | Description | Notes |
| ---------------- | ------- | ----------- | ----- |
| **trigger_name** | **str** |             |

## Example

```python
from authoring_client.models.one_time_trigger_request import OneTimeTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of OneTimeTriggerRequest from a JSON string
one_time_trigger_request_instance = OneTimeTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(OneTimeTriggerRequest.to_json())

# convert the object into a dict
one_time_trigger_request_dict = one_time_trigger_request_instance.to_dict()
# create an instance of OneTimeTriggerRequest from a dict
one_time_trigger_request_from_dict = OneTimeTriggerRequest.from_dict(one_time_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
