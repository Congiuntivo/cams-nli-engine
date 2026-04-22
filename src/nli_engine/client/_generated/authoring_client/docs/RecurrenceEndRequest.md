# RecurrenceEndRequest

## Properties

| Name             | Type                                      | Description | Notes      |
| ---------------- | ----------------------------------------- | ----------- | ---------- |
| **type**         | **str**                                   |             |
| **elapsed_time** | [**DurationRequest**](DurationRequest.md) |             | [optional] |
| **count**        | **int**                                   |             | [optional] |

## Example

```python
from authoring_client.models.recurrence_end_request import RecurrenceEndRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RecurrenceEndRequest from a JSON string
recurrence_end_request_instance = RecurrenceEndRequest.from_json(json)
# print the JSON string representation of the object
print(RecurrenceEndRequest.to_json())

# convert the object into a dict
recurrence_end_request_dict = recurrence_end_request_instance.to_dict()
# create an instance of RecurrenceEndRequest from a dict
recurrence_end_request_from_dict = RecurrenceEndRequest.from_dict(recurrence_end_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
