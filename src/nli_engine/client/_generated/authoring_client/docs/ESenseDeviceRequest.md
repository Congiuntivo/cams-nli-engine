# ESenseDeviceRequest

## Properties

| Name                         | Type     | Description | Notes      |
| ---------------------------- | -------- | ----------- | ---------- |
| **role_name**                | **str**  |             | [optional] |
| **primary_device_role_name** | **str**  |             |
| **is_optional**              | **bool** |             | [optional] |
| **sampling_rate**            | **int**  |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.e_sense_device_request import ESenseDeviceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ESenseDeviceRequest from a JSON string
e_sense_device_request_instance = ESenseDeviceRequest.from_json(json)
# print the JSON string representation of the object
print(ESenseDeviceRequest.to_json())

# convert the object into a dict
e_sense_device_request_dict = e_sense_device_request_instance.to_dict()
# create an instance of ESenseDeviceRequest from a dict
e_sense_device_request_from_dict = ESenseDeviceRequest.from_dict(e_sense_device_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
