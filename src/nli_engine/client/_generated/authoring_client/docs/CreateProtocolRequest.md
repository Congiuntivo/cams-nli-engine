# CreateProtocolRequest

## Properties

| Name                     | Type    | Description | Notes      |
| ------------------------ | ------- | ----------- | ---------- |
| **name**                 | **str** |             |
| **owner_id**             | **str** |             | [optional] |
| **protocol_version_tag** | **str** |             | [optional] |
| **protocol_api_level**   | **str** |             | [optional] |
| **application_name**     | **str** |             | [optional] |
| **privacy_schema_name**  | **str** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.create_protocol_request import CreateProtocolRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateProtocolRequest from a JSON string
create_protocol_request_instance = CreateProtocolRequest.from_json(json)
# print the JSON string representation of the object
print(CreateProtocolRequest.to_json())

# convert the object into a dict
create_protocol_request_dict = create_protocol_request_instance.to_dict()
# create an instance of CreateProtocolRequest from a dict
create_protocol_request_from_dict = CreateProtocolRequest.from_dict(create_protocol_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
