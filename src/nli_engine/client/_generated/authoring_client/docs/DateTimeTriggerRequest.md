# DateTimeTriggerRequest

## Properties

| Name             | Type    | Description | Notes |
| ---------------- | ------- | ----------- | ----- |
| **trigger_name** | **str** |             |
| **schedule**     | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.date_time_trigger_request import DateTimeTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DateTimeTriggerRequest from a JSON string
date_time_trigger_request_instance = DateTimeTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(DateTimeTriggerRequest.to_json())

# convert the object into a dict
date_time_trigger_request_dict = date_time_trigger_request_instance.to_dict()
# create an instance of DateTimeTriggerRequest from a dict
date_time_trigger_request_from_dict = DateTimeTriggerRequest.from_dict(date_time_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
