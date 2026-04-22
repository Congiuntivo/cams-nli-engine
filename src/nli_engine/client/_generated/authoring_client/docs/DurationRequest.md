# DurationRequest

## Properties

| Name             | Type    | Description | Notes      |
| ---------------- | ------- | ----------- | ---------- |
| **days**         | **int** |             | [optional] |
| **hours**        | **int** |             | [optional] |
| **minutes**      | **int** |             | [optional] |
| **seconds**      | **int** |             | [optional] |
| **milliseconds** | **int** |             | [optional] |
| **microseconds** | **int** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.duration_request import DurationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DurationRequest from a JSON string
duration_request_instance = DurationRequest.from_json(json)
# print the JSON string representation of the object
print(DurationRequest.to_json())

# convert the object into a dict
duration_request_dict = duration_request_instance.to_dict()
# create an instance of DurationRequest from a dict
duration_request_from_dict = DurationRequest.from_dict(duration_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
