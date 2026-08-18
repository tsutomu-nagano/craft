from app.repositories.skill_repository import SkillRepository


class SkillService:
    def __init__(self, repository: SkillRepository) -> None:
        self.repository = repository

    def get_version(self, name: str) -> str:
        return self.repository.version(name)
