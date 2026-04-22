# TriggersResponse

## Properties

| Name         | Type                                          | Description | Notes |
| ------------ | --------------------------------------------- | ----------- | ----- |
| **triggers** | [**List[TriggerSummary]**](TriggerSummary.md) |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.triggers_response import TriggersResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TriggersResponse from a JSON string
triggers_response_instance = TriggersResponse.from_json(json)
# print the JSON string representation of the object
print(TriggersResponse.to_json())

# convert the object into a dict
triggers_response_dict = triggers_response_instance.to_dict()
# create an instance of TriggersResponse from a dict
triggers_response_from_dict = TriggersResponse.from_dict(triggers_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
