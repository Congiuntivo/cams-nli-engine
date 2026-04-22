# DelayedTriggerRequest

## Properties

| Name             | Type                                      | Description | Notes |
| ---------------- | ----------------------------------------- | ----------- | ----- |
| **trigger_name** | **str**                                   |             |
| **delay**        | [**DurationRequest**](DurationRequest.md) |             |

## Example

```python
from authoring_client.models.delayed_trigger_request import DelayedTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DelayedTriggerRequest from a JSON string
delayed_trigger_request_instance = DelayedTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(DelayedTriggerRequest.to_json())

# convert the object into a dict
delayed_trigger_request_dict = delayed_trigger_request_instance.to_dict()
# create an instance of DelayedTriggerRequest from a dict
delayed_trigger_request_from_dict = DelayedTriggerRequest.from_dict(delayed_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
