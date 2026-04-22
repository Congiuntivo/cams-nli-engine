# MovesenseDeviceRequest

## Properties

| Name                         | Type     | Description | Notes      |
| ---------------------------- | -------- | ----------- | ---------- |
| **role_name**                | **str**  |             | [optional] |
| **primary_device_role_name** | **str**  |             |
| **is_optional**              | **bool** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.movesense_device_request import MovesenseDeviceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MovesenseDeviceRequest from a JSON string
movesense_device_request_instance = MovesenseDeviceRequest.from_json(json)
# print the JSON string representation of the object
print(MovesenseDeviceRequest.to_json())

# convert the object into a dict
movesense_device_request_dict = movesense_device_request_instance.to_dict()
# create an instance of MovesenseDeviceRequest from a dict
movesense_device_request_from_dict = MovesenseDeviceRequest.from_dict(movesense_device_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
