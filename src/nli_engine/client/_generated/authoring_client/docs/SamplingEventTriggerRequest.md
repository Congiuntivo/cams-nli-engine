# SamplingEventTriggerRequest

## Properties

| Name                  | Type                                                          | Description | Notes      |
| --------------------- | ------------------------------------------------------------- | ----------- | ---------- |
| **trigger_name**      | **str**                                                       |             |
| **measure_type**      | **str**                                                       |             |
| **trigger_condition** | [**SerializedCarpDataRequest**](SerializedCarpDataRequest.md) |             | [optional] |

## Example

```python
from authoring_client.models.sampling_event_trigger_request import SamplingEventTriggerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SamplingEventTriggerRequest from a JSON string
sampling_event_trigger_request_instance = SamplingEventTriggerRequest.from_json(json)
# print the JSON string representation of the object
print(SamplingEventTriggerRequest.to_json())

# convert the object into a dict
sampling_event_trigger_request_dict = sampling_event_trigger_request_instance.to_dict()
# create an instance of SamplingEventTriggerRequest from a dict
sampling_event_trigger_request_from_dict = SamplingEventTriggerRequest.from_dict(sampling_event_trigger_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
