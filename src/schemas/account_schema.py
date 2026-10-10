from typing import Literal

from pydantic import BaseModel, ConfigDict, constr


class AccountPatchSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ACTIVE", "BLOCKED", "CLOSED"]
    reason: constr(max_length=255) | None = None
