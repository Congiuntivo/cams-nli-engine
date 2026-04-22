# RecurrentScheduledTriggerRequest

## Properties

| Name                       | Type                                        | Description | Notes      |
| -------------------------- | ------------------------------------------- | ----------- | ---------- |
| **trigger_name**           | **str**                                     |             |
| **type**                   | **str**                                     |             |
| **time**                   | [**TimeOfDayRequest**](TimeOfDayRequest.md) |             |
| **end**                    | **str**                                     |             | [optional] |
| **separation_count**       | **int**                                     |             | [optional] |
| **max_number_of_sampling** | **int**                                     |             | [optional] |
| **day_of_week**            | **int**                                     |             | [optional] |
| **week_of_month**          | **int**                                     |             | [optional] |
| **day_of_month**           | **int**                                     |             | [optional] |
| **duration**               | [**DurationRequest**](DurationRequest.md)   |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.recurrent_scheduled_trigger_request import RecurrentScheduledTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RecurrentScheduledTriggerRequest from a JSON string
recurrent_scheduled_trigger_request_instance = RecurrentScheduledTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(RecurrentScheduledTriggerRequest.to_json())

# convert the object into a dict
recurrent_scheduled_trigger_request_dict = recurrent_scheduled_trigger_request_instance.to_dict()
# create an instance of RecurrentScheduledTriggerRequest from a dict
recurrent_scheduled_trigger_request_from_dict = RecurrentScheduledTriggerRequest.from_dict(recurrent_scheduled_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
