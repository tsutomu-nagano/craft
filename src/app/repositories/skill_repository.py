from pathlib import Path


class SkillRepository:
    def version(self, name: str) -> str:
        skill_file = Path("skills") / name / "SKILL.md"
        if not skill_file.exists():
            return "none"
        for line in skill_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip()
        return "unversioned"
