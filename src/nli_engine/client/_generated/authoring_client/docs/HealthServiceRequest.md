# HealthServiceRequest

## Properties

| Name                         | Type    | Description | Notes      |
| ---------------------------- | ------- | ----------- | ---------- |
| **role_name**                | **str** |             | [optional] |
| **primary_device_role_name** | **str** |             |

## Example

```python
from nli_engine.client._generated.authoring_client.models.health_service_request import HealthServiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HealthServiceRequest from a JSON string
health_service_request_instance = HealthServiceRequest.from_json(json)
# print the JSON string representation of the object
print(HealthServiceRequest.to_json())

# convert the object into a dict
health_service_request_dict = health_service_request_instance.to_dict()
# create an instance of HealthServiceRequest from a dict
health_service_request_from_dict = HealthServiceRequest.from_dict(health_service_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
