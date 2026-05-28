# BaseConnectedDeviceRequest

## Properties

| Name                         | Type    | Description | Notes      |
| ---------------------------- | ------- | ----------- | ---------- |
| **role_name**                | **str** |             | [optional] |
| **primary_device_role_name** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.base_connected_device_request import BaseConnectedDeviceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BaseConnectedDeviceRequest from a JSON string
base_connected_device_request_instance = BaseConnectedDeviceRequest.from_json(json)
# print the JSON string representation of the object
print(BaseConnectedDeviceRequest.to_json())

# convert the object into a dict
base_connected_device_request_dict = base_connected_device_request_instance.to_dict()
# create an instance of BaseConnectedDeviceRequest from a dict
base_connected_device_request_from_dict = BaseConnectedDeviceRequest.from_dict(base_connected_device_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
