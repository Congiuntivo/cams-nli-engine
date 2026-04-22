# PolarDeviceRequest

## Properties

| Name                         | Type     | Description | Notes      |
| ---------------------------- | -------- | ----------- | ---------- |
| **role_name**                | **str**  |             | [optional] |
| **primary_device_role_name** | **str**  |             |
| **is_optional**              | **bool** |             | [optional] |
| **name_prefix**              | **str**  |             | [optional] |

## Example

```python
from authoring_client.models.polar_device_request import PolarDeviceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PolarDeviceRequest from a JSON string
polar_device_request_instance = PolarDeviceRequest.from_json(json)
# print the JSON string representation of the object
print(PolarDeviceRequest.to_json())

# convert the object into a dict
polar_device_request_dict = polar_device_request_instance.to_dict()
# create an instance of PolarDeviceRequest from a dict
polar_device_request_from_dict = PolarDeviceRequest.from_dict(polar_device_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
