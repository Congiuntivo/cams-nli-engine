# WeatherServiceRequest

## Properties

| Name                         | Type    | Description | Notes      |
| ---------------------------- | ------- | ----------- | ---------- |
| **role_name**                | **str** |             | [optional] |
| **primary_device_role_name** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.weather_service_request import WeatherServiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WeatherServiceRequest from a JSON string
weather_service_request_instance = WeatherServiceRequest.from_json(json)
# print the JSON string representation of the object
print(WeatherServiceRequest.to_json())

# convert the object into a dict
weather_service_request_dict = weather_service_request_instance.to_dict()
# create an instance of WeatherServiceRequest from a dict
weather_service_request_from_dict = WeatherServiceRequest.from_dict(weather_service_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
