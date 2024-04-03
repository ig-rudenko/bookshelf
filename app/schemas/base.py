from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class BaseConfigModel(BaseModel):
    class Config:
        from_attributes = True
        alias_generator = to_camel
