# TriggerSummary

## Properties

| Name        | Type                  | Description | Notes |
| ----------- | --------------------- | ----------- | ----- |
| **name**    | **str**               |             |
| **trigger** | **Dict[str, object]** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.trigger_summary import TriggerSummary

# TODO update the JSON string below
json = "{}"
# create an instance of TriggerSummary from a JSON string
trigger_summary_instance = TriggerSummary.from_json(json)
# print the JSON string representation of the object
print(TriggerSummary.to_json())

# convert the object into a dict
trigger_summary_dict = trigger_summary_instance.to_dict()
# create an instance of TriggerSummary from a dict
trigger_summary_from_dict = TriggerSummary.from_dict(trigger_summary_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
