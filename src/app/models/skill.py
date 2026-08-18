from pydantic import BaseModel


class SkillVersion(BaseModel):
    name: str
    version: str
