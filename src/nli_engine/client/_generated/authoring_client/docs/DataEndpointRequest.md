# DataEndpointRequest

## Properties

| Name                     | Type     | Description | Notes      |
| ------------------------ | -------- | ----------- | ---------- |
| **endpoint_type**        | **str**  |             |
| **upload_method**        | **str**  |             | [optional] |
| **name**                 | **str**  |             | [optional] |
| **delete_when_uploaded** | **bool** |             | [optional] |
| **buffer_size**          | **int**  |             | [optional] |
| **zip**                  | **bool** |             | [optional] |
| **encrypt**              | **bool** |             | [optional] |
| **public_key**           | **str**  |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.data_endpoint_request import DataEndpointRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DataEndpointRequest from a JSON string
data_endpoint_request_instance = DataEndpointRequest.from_json(json)
# print the JSON string representation of the object
print(DataEndpointRequest.to_json())

# convert the object into a dict
data_endpoint_request_dict = data_endpoint_request_instance.to_dict()
# create an instance of DataEndpointRequest from a dict
data_endpoint_request_from_dict = DataEndpointRequest.from_dict(data_endpoint_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
