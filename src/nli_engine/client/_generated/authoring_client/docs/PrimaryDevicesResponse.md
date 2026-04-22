# PrimaryDevicesResponse

## Properties

| Name                | Type                                    | Description | Notes |
| ------------------- | --------------------------------------- | ----------- | ----- |
| **primary_devices** | [**List[NamedDevice]**](NamedDevice.md) |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.primary_devices_response import PrimaryDevicesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PrimaryDevicesResponse from a JSON string
primary_devices_response_instance = PrimaryDevicesResponse.from_json(json)
# print the JSON string representation of the object
print(PrimaryDevicesResponse.to_json())

# convert the object into a dict
primary_devices_response_dict = primary_devices_response_instance.to_dict()
# create an instance of PrimaryDevicesResponse from a dict
primary_devices_response_from_dict = PrimaryDevicesResponse.from_dict(primary_devices_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
