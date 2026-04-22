# PrimaryDeviceRoleRequest

## Properties

| Name          | Type    | Description | Notes      |
| ------------- | ------- | ----------- | ---------- |
| **role_name** | **str** |             | [optional] |

## Example

```python
from authoring_client.models.primary_device_role_request import PrimaryDeviceRoleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PrimaryDeviceRoleRequest from a JSON string
primary_device_role_request_instance = PrimaryDeviceRoleRequest.from_json(json)
# print the JSON string representation of the object
print(PrimaryDeviceRoleRequest.to_json())

# convert the object into a dict
primary_device_role_request_dict = primary_device_role_request_instance.to_dict()
# create an instance of PrimaryDeviceRoleRequest from a dict
primary_device_role_request_from_dict = PrimaryDeviceRoleRequest.from_dict(primary_device_role_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
