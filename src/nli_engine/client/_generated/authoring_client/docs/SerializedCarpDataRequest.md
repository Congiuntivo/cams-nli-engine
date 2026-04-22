# SerializedCarpDataRequest

## Properties

| Name     | Type    | Description | Notes |
| -------- | ------- | ----------- | ----- |
| **type** | **str** |             |

## Example

```python
from authoring_client.models.serialized_carp_data_request import SerializedCarpDataRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SerializedCarpDataRequest from a JSON string
serialized_carp_data_request_instance = SerializedCarpDataRequest.from_json(json)
# print the JSON string representation of the object
print(SerializedCarpDataRequest.to_json())

# convert the object into a dict
serialized_carp_data_request_dict = serialized_carp_data_request_instance.to_dict()
# create an instance of SerializedCarpDataRequest from a dict
serialized_carp_data_request_from_dict = SerializedCarpDataRequest.from_dict(serialized_carp_data_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
