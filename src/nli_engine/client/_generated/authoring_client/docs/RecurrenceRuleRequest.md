# RecurrenceRuleRequest

## Properties

| Name          | Type                                                | Description | Notes      |
| ------------- | --------------------------------------------------- | ----------- | ---------- |
| **frequency** | **str**                                             |             |
| **interval**  | **int**                                             |             | [optional] |
| **end**       | [**RecurrenceEndRequest**](RecurrenceEndRequest.md) |             | [optional] |

## Example

```python
from authoring_client.models.recurrence_rule_request import RecurrenceRuleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RecurrenceRuleRequest from a JSON string
recurrence_rule_request_instance = RecurrenceRuleRequest.from_json(json)
# print the JSON string representation of the object
print(RecurrenceRuleRequest.to_json())

# convert the object into a dict
recurrence_rule_request_dict = recurrence_rule_request_instance.to_dict()
# create an instance of RecurrenceRuleRequest from a dict
recurrence_rule_request_from_dict = RecurrenceRuleRequest.from_dict(recurrence_rule_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
