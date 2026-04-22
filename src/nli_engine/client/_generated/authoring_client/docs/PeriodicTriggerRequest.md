# PeriodicTriggerRequest

## Properties

| Name             | Type                                      | Description | Notes |
| ---------------- | ----------------------------------------- | ----------- | ----- |
| **trigger_name** | **str**                                   |             |
| **period**       | [**DurationRequest**](DurationRequest.md) |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.periodic_trigger_request import PeriodicTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PeriodicTriggerRequest from a JSON string
periodic_trigger_request_instance = PeriodicTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(PeriodicTriggerRequest.to_json())

# convert the object into a dict
periodic_trigger_request_dict = periodic_trigger_request_instance.to_dict()
# create an instance of PeriodicTriggerRequest from a dict
periodic_trigger_request_from_dict = PeriodicTriggerRequest.from_dict(periodic_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
