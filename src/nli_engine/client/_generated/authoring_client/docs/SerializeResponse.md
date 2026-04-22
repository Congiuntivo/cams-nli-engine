# SerializeResponse

## Properties

| Name                  | Type             | Description | Notes      |
| --------------------- | ---------------- | ----------- | ---------- |
| **name**              | **str**          |             |
| **owner_id**          | **str**          |             |
| **version**           | **int**          |             |
| **id**                | **str**          |             | [optional] |
| **created_on**        | **str**          |             | [optional] |
| **description**       | **str**          |             | [optional] |
| **participant_roles** | **List[object]** |             | [optional] |
| **primary_devices**   | **List[object]** |             | [optional] |
| **connected_devices** | **List[object]** |             | [optional] |
| **tasks**             | **List[object]** |             | [optional] |
| **triggers**          | **List[object]** |             | [optional] |
| **task_controls**     | **List[object]** |             | [optional] |

## Example

```python
from authoring_client.models.serialize_response import SerializeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SerializeResponse from a JSON string
serialize_response_instance = SerializeResponse.from_json(json)
# print the JSON string representation of the object
print(SerializeResponse.to_json())

# convert the object into a dict
serialize_response_dict = serialize_response_instance.to_dict()
# create an instance of SerializeResponse from a dict
serialize_response_from_dict = SerializeResponse.from_dict(serialize_response_dict)
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
