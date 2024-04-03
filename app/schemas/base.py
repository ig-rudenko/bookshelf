from pydantic import BaseModel, AliasGenerator
from pydantic.alias_generators import to_camel


class CamelSerializerModel(BaseModel):
    class Config:
        from_attributes = True
        alias_generator = AliasGenerator(
            validation_alias=lambda x: x,
            serialization_alias=to_camel,
        )


class CamelAliasModel(BaseModel):
    class Config:
        alias_generator = to_camel
