# WebTaskRequest

## Properties

| Name            | Type                                                  | Description | Notes |
| --------------- | ----------------------------------------------------- | ----------- | ----- |
| **name**        | **str**                                               |             |
| **description** | **str**                                               |             |
| **measures**    | [**List[TaskMeasureRequest]**](TaskMeasureRequest.md) |             |
| **url**         | **str**                                               |             |

## Example

```python
from authoring_client.models.web_task_request import WebTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WebTaskRequest from a JSON string
web_task_request_instance = WebTaskRequest.from_json(json)
# print the JSON string representation of the object
print(WebTaskRequest.to_json())

# convert the object into a dict
web_task_request_dict = web_task_request_instance.to_dict()
# create an instance of WebTaskRequest from a dict
web_task_request_from_dict = WebTaskRequest.from_dict(web_task_request_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
