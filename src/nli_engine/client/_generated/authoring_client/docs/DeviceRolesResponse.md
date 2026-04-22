# DeviceRolesResponse

## Properties

| Name        | Type                                    | Description | Notes |
| ----------- | --------------------------------------- | ----------- | ----- |
| **devices** | [**List[NamedDevice]**](NamedDevice.md) |             |

## Example

```python
from authoring_client.models.device_roles_response import DeviceRolesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceRolesResponse from a JSON string
device_roles_response_instance = DeviceRolesResponse.from_json(json)
# print the JSON string representation of the object
print(DeviceRolesResponse.to_json())

# convert the object into a dict
device_roles_response_dict = device_roles_response_instance.to_dict()
# create an instance of DeviceRolesResponse from a dict
device_roles_response_from_dict = DeviceRolesResponse.from_dict(device_roles_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
