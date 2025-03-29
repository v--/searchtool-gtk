import pydantic


class StrictPydanticModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='forbid')
