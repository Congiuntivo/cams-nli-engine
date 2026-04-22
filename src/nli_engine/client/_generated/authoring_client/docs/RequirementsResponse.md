# RequirementsResponse

## Properties

| Name                         | Type       | Description | Notes |
| ---------------------------- | ---------- | ----------- | ----- |
| **unfulfilled_requirements** | **object** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.requirements_response import RequirementsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RequirementsResponse from a JSON string
requirements_response_instance = RequirementsResponse.from_json(json)
# print the JSON string representation of the object
print(RequirementsResponse.to_json())

# convert the object into a dict
requirements_response_dict = requirements_response_instance.to_dict()
# create an instance of RequirementsResponse from a dict
requirements_response_from_dict = RequirementsResponse.from_dict(requirements_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
