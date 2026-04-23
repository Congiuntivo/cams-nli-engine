# AddExpectedParticipantDataRequest

## Properties

| Name          | Type    | Description | Notes |
| ------------- | ------- | ----------- | ----- |
| **data_type** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.add_expected_participant_data_request import AddExpectedParticipantDataRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddExpectedParticipantDataRequest from a JSON string
add_expected_participant_data_request_instance = AddExpectedParticipantDataRequest.from_json(json)
# print the JSON string representation of the object
print(AddExpectedParticipantDataRequest.to_json())

# convert the object into a dict
add_expected_participant_data_request_dict = add_expected_participant_data_request_instance.to_dict()
# create an instance of AddExpectedParticipantDataRequest from a dict
add_expected_participant_data_request_from_dict = AddExpectedParticipantDataRequest.from_dict(add_expected_participant_data_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
