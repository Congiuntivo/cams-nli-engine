# LocationServiceRequest

## Properties

| Name                                   | Type                                      | Description | Notes      |
| -------------------------------------- | ----------------------------------------- | ----------- | ---------- |
| **role_name**                          | **str**                                   |             | [optional] |
| **primary_device_role_name**           | **str**                                   |             |
| **accuracy**                           | **str**                                   |             | [optional] |
| **distance**                           | **float**                                 |             | [optional] |
| **interval**                           | [**DurationRequest**](DurationRequest.md) |             | [optional] |
| **notification_title**                 | **str**                                   |             | [optional] |
| **notification_message**               | **str**                                   |             | [optional] |
| **notification_description**           | **str**                                   |             | [optional] |
| **notification_icon_name**             | **str**                                   |             | [optional] |
| **notification_on_tap_bring_to_front** | **bool**                                  |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.location_service_request import LocationServiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LocationServiceRequest from a JSON string
location_service_request_instance = LocationServiceRequest.from_json(json)
# print the JSON string representation of the object
print(LocationServiceRequest.to_json())

# convert the object into a dict
location_service_request_dict = location_service_request_instance.to_dict()
# create an instance of LocationServiceRequest from a dict
location_service_request_from_dict = LocationServiceRequest.from_dict(location_service_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
