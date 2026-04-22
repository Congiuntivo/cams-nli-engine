# ParticipantRolesResponse

## Properties

| Name           | Type          | Description | Notes |
| -------------- | ------------- | ----------- | ----- |
| **role_names** | **List[str]** |             |

## Example

```python
from authoring_client.models.participant_roles_response import ParticipantRolesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ParticipantRolesResponse from a JSON string
participant_roles_response_instance = ParticipantRolesResponse.from_json(json)
# print the JSON string representation of the object
print(ParticipantRolesResponse.to_json())

# convert the object into a dict
participant_roles_response_dict = participant_roles_response_instance.to_dict()
# create an instance of ParticipantRolesResponse from a dict
participant_roles_response_from_dict = ParticipantRolesResponse.from_dict(participant_roles_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
