# AirQualityServiceRequest

## Properties

| Name                         | Type    | Description | Notes      |
| ---------------------------- | ------- | ----------- | ---------- |
| **role_name**                | **str** |             | [optional] |
| **primary_device_role_name** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.air_quality_service_request import AirQualityServiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AirQualityServiceRequest from a JSON string
air_quality_service_request_instance = AirQualityServiceRequest.from_json(json)
# print the JSON string representation of the object
print(AirQualityServiceRequest.to_json())

# convert the object into a dict
air_quality_service_request_dict = air_quality_service_request_instance.to_dict()
# create an instance of AirQualityServiceRequest from a dict
air_quality_service_request_from_dict = AirQualityServiceRequest.from_dict(air_quality_service_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
