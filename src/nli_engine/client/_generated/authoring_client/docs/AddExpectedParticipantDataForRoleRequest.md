# AddExpectedParticipantDataForRoleRequest

## Properties

| Name          | Type                                              | Description | Notes |
| ------------- | ------------------------------------------------- | ----------- | ----- |
| **role_name** | **str**                                           |             |
| **data_type** | [**ParticipantDataType**](ParticipantDataType.md) |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.add_expected_participant_data_for_role_request import AddExpectedParticipantDataForRoleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddExpectedParticipantDataForRoleRequest from a JSON string
add_expected_participant_data_for_role_request_instance = AddExpectedParticipantDataForRoleRequest.from_json(json)
# print the JSON string representation of the object
print(AddExpectedParticipantDataForRoleRequest.to_json())

# convert the object into a dict
add_expected_participant_data_for_role_request_dict = add_expected_participant_data_for_role_request_instance.to_dict()
# create an instance of AddExpectedParticipantDataForRoleRequest from a dict
add_expected_participant_data_for_role_request_from_dict = AddExpectedParticipantDataForRoleRequest.from_dict(add_expected_participant_data_for_role_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
