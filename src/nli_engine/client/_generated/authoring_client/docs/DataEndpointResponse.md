# DataEndpointResponse

## Properties

| Name                         | Type       | Description | Notes |
| ---------------------------- | ---------- | ----------- | ----- |
| **session_id**               | **str**    |             |
| **unfulfilled_requirements** | **object** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.data_endpoint_response import DataEndpointResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DataEndpointResponse from a JSON string
data_endpoint_response_instance = DataEndpointResponse.from_json(json)
# print the JSON string representation of the object
print(DataEndpointResponse.to_json())

# convert the object into a dict
data_endpoint_response_dict = data_endpoint_response_instance.to_dict()
# create an instance of DataEndpointResponse from a dict
data_endpoint_response_from_dict = DataEndpointResponse.from_dict(data_endpoint_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
