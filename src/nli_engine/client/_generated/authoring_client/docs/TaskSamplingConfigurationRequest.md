# TaskSamplingConfigurationRequest

## Properties

| Name                   | Type                                      | Description | Notes      |
| ---------------------- | ----------------------------------------- | ----------- | ---------- |
| **sampling_type**      | **str**                                   |             |
| **interval**           | [**DurationRequest**](DurationRequest.md) |             | [optional] |
| **duration**           | [**DurationRequest**](DurationRequest.md) |             | [optional] |
| **once**               | **bool**                                  |             | [optional] |
| **use_prior_contexts** | **bool**                                  |             | [optional] |
| **stop_radius**        | **float**                                 |             | [optional] |
| **place_radius**       | **float**                                 |             | [optional] |
| **stop_duration**      | [**DurationRequest**](DurationRequest.md) |             | [optional] |

## Example

```python
from nli_engine.client._generated.authoring_client.models.task_sampling_configuration_request import TaskSamplingConfigurationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TaskSamplingConfigurationRequest from a JSON string
task_sampling_configuration_request_instance = TaskSamplingConfigurationRequest.from_json(json)
# print the JSON string representation of the object
print(TaskSamplingConfigurationRequest.to_json())

# convert the object into a dict
task_sampling_configuration_request_dict = task_sampling_configuration_request_instance.to_dict()
# create an instance of TaskSamplingConfigurationRequest from a dict
task_sampling_configuration_request_from_dict = TaskSamplingConfigurationRequest.from_dict(task_sampling_configuration_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
