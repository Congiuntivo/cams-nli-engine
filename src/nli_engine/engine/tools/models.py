from typing import Optional

from pydantic import BaseModel


class AddParticipantRoleRequest(BaseModel):
    role_name: str
    is_optional: bool = False


class AddExpectedDataAllRolesRequest(BaseModel):
    data_type: str


class AddExpectedDataForRoleRequest(BaseModel):
    role_name: str
    data_type: str


class AddSimpleServiceRequest(BaseModel):
    primary_device_role_name: str
    role_name: Optional[str] = None
