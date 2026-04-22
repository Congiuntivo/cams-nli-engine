# CronScheduledTriggerRequest

## Properties

| Name             | Type    | Description | Notes      |
| ---------------- | ------- | ----------- | ---------- |
| **trigger_name** | **str** |             |
| **minute**       | **int** |             | [optional] |
| **hour**         | **int** |             | [optional] |
| **day**          | **int** |             | [optional] |
| **month**        | **int** |             | [optional] |
| **weekday**      | **int** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.cron_scheduled_trigger_request import CronScheduledTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CronScheduledTriggerRequest from a JSON string
cron_scheduled_trigger_request_instance = CronScheduledTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(CronScheduledTriggerRequest.to_json())

# convert the object into a dict
cron_scheduled_trigger_request_dict = cron_scheduled_trigger_request_instance.to_dict()
# create an instance of CronScheduledTriggerRequest from a dict
cron_scheduled_trigger_request_from_dict = CronScheduledTriggerRequest.from_dict(cron_scheduled_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
