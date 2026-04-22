# TimeOfDayRequest

## Properties

| Name       | Type    | Description | Notes      |
| ---------- | ------- | ----------- | ---------- |
| **hour**   | **int** |             |
| **minute** | **int** |             |
| **second** | **int** |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.time_of_day_request import TimeOfDayRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TimeOfDayRequest from a JSON string
time_of_day_request_instance = TimeOfDayRequest.from_json(json)
# print the JSON string representation of the object
print(TimeOfDayRequest.to_json())

# convert the object into a dict
time_of_day_request_dict = time_of_day_request_instance.to_dict()
# create an instance of TimeOfDayRequest from a dict
time_of_day_request_from_dict = TimeOfDayRequest.from_dict(time_of_day_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
