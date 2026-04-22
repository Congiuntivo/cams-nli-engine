# ElapsedTimeTriggerRequest

## Properties

| Name             | Type                                      | Description | Notes |
| ---------------- | ----------------------------------------- | ----------- | ----- |
| **trigger_name** | **str**                                   |             |
| **elapsed_time** | [**DurationRequest**](DurationRequest.md) |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.elapsed_time_trigger_request import ElapsedTimeTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ElapsedTimeTriggerRequest from a JSON string
elapsed_time_trigger_request_instance = ElapsedTimeTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(ElapsedTimeTriggerRequest.to_json())

# convert the object into a dict
elapsed_time_trigger_request_dict = elapsed_time_trigger_request_instance.to_dict()
# create an instance of ElapsedTimeTriggerRequest from a dict
elapsed_time_trigger_request_from_dict = ElapsedTimeTriggerRequest.from_dict(elapsed_time_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
