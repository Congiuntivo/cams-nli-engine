# ScheduledTriggerRequest

## Properties

| Name                | Type                                                  | Description | Notes |
| ------------------- | ----------------------------------------------------- | ----------- | ----- |
| **trigger_name**    | **str**                                               |             |
| **time**            | [**TimeOfDayRequest**](TimeOfDayRequest.md)           |             |
| **recurrence_rule** | [**RecurrenceRuleRequest**](RecurrenceRuleRequest.md) |             |

## Example

```python
from authoring_client.models.scheduled_trigger_request import ScheduledTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ScheduledTriggerRequest from a JSON string
scheduled_trigger_request_instance = ScheduledTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(ScheduledTriggerRequest.to_json())

# convert the object into a dict
scheduled_trigger_request_dict = scheduled_trigger_request_instance.to_dict()
# create an instance of ScheduledTriggerRequest from a dict
scheduled_trigger_request_from_dict = ScheduledTriggerRequest.from_dict(scheduled_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
