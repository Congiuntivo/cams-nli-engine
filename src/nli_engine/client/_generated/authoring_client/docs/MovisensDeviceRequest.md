# MovisensDeviceRequest

## Properties

| Name                         | Type    | Description | Notes      |
| ---------------------------- | ------- | ----------- | ---------- |
| **role_name**                | **str** |             | [optional] |
| **primary_device_role_name** | **str** |             |
| **sensor_location**          | **str** |             | [optional] |
| **sex**                      | **str** |             | [optional] |
| **height**                   | **int** |             | [optional] |
| **weight**                   | **int** |             | [optional] |
| **age**                      | **int** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.movisens_device_request import MovisensDeviceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MovisensDeviceRequest from a JSON string
movisens_device_request_instance = MovisensDeviceRequest.from_json(json)
# print the JSON string representation of the object
print(MovisensDeviceRequest.to_json())

# convert the object into a dict
movisens_device_request_dict = movisens_device_request_instance.to_dict()
# create an instance of MovisensDeviceRequest from a dict
movisens_device_request_from_dict = MovisensDeviceRequest.from_dict(movisens_device_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
