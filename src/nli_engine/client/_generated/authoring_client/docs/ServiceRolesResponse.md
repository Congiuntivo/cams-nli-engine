# ServiceRolesResponse

## Properties

| Name         | Type                                    | Description | Notes |
| ------------ | --------------------------------------- | ----------- | ----- |
| **services** | [**List[NamedDevice]**](NamedDevice.md) |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.service_roles_response import ServiceRolesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceRolesResponse from a JSON string
service_roles_response_instance = ServiceRolesResponse.from_json(json)
# print the JSON string representation of the object
print(ServiceRolesResponse.to_json())

# convert the object into a dict
service_roles_response_dict = service_roles_response_instance.to_dict()
# create an instance of ServiceRolesResponse from a dict
service_roles_response_from_dict = ServiceRolesResponse.from_dict(service_roles_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
