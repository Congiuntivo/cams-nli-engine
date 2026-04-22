# TaskMeasureRequest

## Properties

| Name                       | Type                                                                        | Description | Notes      |
| -------------------------- | --------------------------------------------------------------------------- | ----------- | ---------- |
| **measure_type**           | **str**                                                                     |             |
| **sampling_configuration** | [**TaskSamplingConfigurationRequest**](TaskSamplingConfigurationRequest.md) |             | [optional] |

## Example

```python
from authoring_client.models.task_measure_request import TaskMeasureRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TaskMeasureRequest from a JSON string
task_measure_request_instance = TaskMeasureRequest.from_json(json)
# print the JSON string representation of the object
print(TaskMeasureRequest.to_json())

# convert the object into a dict
task_measure_request_dict = task_measure_request_instance.to_dict()
# create an instance of TaskMeasureRequest from a dict
task_measure_request_from_dict = TaskMeasureRequest.from_dict(task_measure_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
