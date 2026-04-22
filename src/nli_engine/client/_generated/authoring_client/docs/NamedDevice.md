# NamedDevice

## Properties

| Name       | Type       | Description | Notes |
| ---------- | ---------- | ----------- | ----- |
| **name**   | **str**    |             |
| **device** | **object** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.named_device import NamedDevice

# TODO update the JSON string below
json = "{}"
# create an instance of NamedDevice from a JSON string
named_device_instance = NamedDevice.from_json(json)
# print the JSON string representation of the object
print(NamedDevice.to_json())

# convert the object into a dict
named_device_dict = named_device_instance.to_dict()
# create an instance of NamedDevice from a dict
named_device_from_dict = NamedDevice.from_dict(named_device_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
