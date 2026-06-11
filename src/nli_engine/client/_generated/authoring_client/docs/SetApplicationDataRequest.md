# SetApplicationDataRequest

## Properties

| Name                 | Type                  | Description | Notes      |
| -------------------- | --------------------- | ----------- | ---------- |
| **application_data** | **Dict[str, object]** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.set_application_data_request import SetApplicationDataRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SetApplicationDataRequest from a JSON string
set_application_data_request_instance = SetApplicationDataRequest.from_json(json)
# print the JSON string representation of the object
print(SetApplicationDataRequest.to_json())

# convert the object into a dict
set_application_data_request_dict = set_application_data_request_instance.to_dict()
# create an instance of SetApplicationDataRequest from a dict
set_application_data_request_from_dict = SetApplicationDataRequest.from_dict(set_application_data_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
