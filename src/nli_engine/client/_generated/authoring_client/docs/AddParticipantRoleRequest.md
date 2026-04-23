# AddParticipantRoleRequest

## Properties

| Name            | Type     | Description | Notes      |
| --------------- | -------- | ----------- | ---------- |
| **role_name**   | **str**  |             |
| **is_optional** | **bool** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.add_participant_role_request import AddParticipantRoleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddParticipantRoleRequest from a JSON string
add_participant_role_request_instance = AddParticipantRoleRequest.from_json(json)
# print the JSON string representation of the object
print(AddParticipantRoleRequest.to_json())

# convert the object into a dict
add_participant_role_request_dict = add_participant_role_request_instance.to_dict()
# create an instance of AddParticipantRoleRequest from a dict
add_participant_role_request_from_dict = AddParticipantRoleRequest.from_dict(add_participant_role_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
