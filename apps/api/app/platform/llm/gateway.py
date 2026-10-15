from typing import Any
from pydantic import BaseModel


class FakeLLM:
    async def generate_structured(
        self, prompt: str, schema: type[BaseModel], **kwargs: Any,
    ) -> BaseModel:
        # Returns a dummy populated model for testing
        dummy_data: dict[str, Any] = {}
        for field_name, field in schema.model_fields.items():
            annotation = field.annotation
            if annotation is str:
                dummy_data[field_name] = "dummy text"
            elif annotation is int:
                dummy_data[field_name] = 1
            elif annotation is list or getattr(annotation, '__origin__', None) is list:
                dummy_data[field_name] = []
            else:
                dummy_data[field_name] = None
        return schema(**dummy_data)

gateway = FakeLLM()
