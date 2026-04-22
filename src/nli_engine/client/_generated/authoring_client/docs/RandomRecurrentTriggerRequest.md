# RandomRecurrentTriggerRequest

## Properties

| Name                       | Type                                        | Description | Notes |
| -------------------------- | ------------------------------------------- | ----------- | ----- |
| **trigger_name**           | **str**                                     |             |
| **min_number_of_triggers** | **int**                                     |             |
| **max_number_of_triggers** | **int**                                     |             |
| **start_time**             | [**TimeOfDayRequest**](TimeOfDayRequest.md) |             |
| **end_time**               | [**TimeOfDayRequest**](TimeOfDayRequest.md) |             |

## Example

```python
from authoring_client.models.random_recurrent_trigger_request import RandomRecurrentTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RandomRecurrentTriggerRequest from a JSON string
random_recurrent_trigger_request_instance = RandomRecurrentTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(RandomRecurrentTriggerRequest.to_json())

# convert the object into a dict
random_recurrent_trigger_request_dict = random_recurrent_trigger_request_instance.to_dict()
# create an instance of RandomRecurrentTriggerRequest from a dict
random_recurrent_trigger_request_from_dict = RandomRecurrentTriggerRequest.from_dict(random_recurrent_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
