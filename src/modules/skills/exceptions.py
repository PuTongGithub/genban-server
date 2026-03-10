"""Skill 模块异常类"""


class SkillException(Exception):
    """Skill 基础异常"""

    def __init__(self, message: str):
        super().__init__(message)


class SkillNotFoundException(SkillException):
    """Skill 不存在异常"""

    def __init__(self, skill_id: str):
        super().__init__(f"Skill 不存在: {skill_id}")


class SkillParseException(SkillException):
    """Skill 解析失败异常"""

    def __init__(self, reason: str):
        super().__init__(f"Skill 解析失败: {reason}")


class SkillAlreadyExistsException(SkillException):
    """Skill 已存在异常"""

    def __init__(self, skill_id: str):
        super().__init__(f"Skill 已存在: {skill_id}")
