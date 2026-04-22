# TaskControlSummary

## Properties

| Name              | Type       | Description | Notes |
| ----------------- | ---------- | ----------- | ----- |
| **task_control**  | **object** |             |
| **trigger**       | **object** |             |
| **task**          | **object** |             |
| **target_device** | **object** |             |

## Example

```python
from authoring_client.models.task_control_summary import TaskControlSummary

# TODO update the JSON string below
json = "{}"
# create an instance of TaskControlSummary from a JSON string
task_control_summary_instance = TaskControlSummary.from_json(json)
# print the JSON string representation of the object
print(TaskControlSummary.to_json())

# convert the object into a dict
task_control_summary_dict = task_control_summary_instance.to_dict()
# create an instance of TaskControlSummary from a dict
task_control_summary_from_dict = TaskControlSummary.from_dict(task_control_summary_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
