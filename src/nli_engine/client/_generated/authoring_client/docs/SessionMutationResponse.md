# SessionMutationResponse

## Properties

| Name                         | Type       | Description | Notes |
| ---------------------------- | ---------- | ----------- | ----- |
| **session_id**               | **str**    |             |
| **unfulfilled_requirements** | **object** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.session_mutation_response import SessionMutationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SessionMutationResponse from a JSON string
session_mutation_response_instance = SessionMutationResponse.from_json(json)
# print the JSON string representation of the object
print(SessionMutationResponse.to_json())

# convert the object into a dict
session_mutation_response_dict = session_mutation_response_instance.to_dict()
# create an instance of SessionMutationResponse from a dict
session_mutation_response_from_dict = SessionMutationResponse.from_dict(session_mutation_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
