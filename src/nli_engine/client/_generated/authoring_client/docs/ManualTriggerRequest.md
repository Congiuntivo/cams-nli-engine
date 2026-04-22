# ManualTriggerRequest

## Properties

| Name             | Type    | Description | Notes      |
| ---------------- | ------- | ----------- | ---------- |
| **trigger_name** | **str** |             |
| **label**        | **str** |             | [optional] |
| **description**  | **str** |             | [optional] |

## Example

```python
from authoring_client.models.manual_trigger_request import ManualTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ManualTriggerRequest from a JSON string
manual_trigger_request_instance = ManualTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(ManualTriggerRequest.to_json())

# convert the object into a dict
manual_trigger_request_dict = manual_trigger_request_instance.to_dict()
# create an instance of ManualTriggerRequest from a dict
manual_trigger_request_from_dict = ManualTriggerRequest.from_dict(manual_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
