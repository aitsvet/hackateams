
from pydantic import BaseModel, Field

class Participant(BaseModel):
    id: str = Field(description="ID пользователя, например user123456789")
    name: str = Field(description="Полное имя, например Иван Петров")
    reactions: list[str] | None = Field(default=None, description="Список ID пользователей, поставивших реакции данному пользователю")
    location: str | None = Field(default=None, description="Город, например Лондон, Берлин, Сан-Франциско")
    availability: str | None = Field(default=None, description="онлайн, оффлайн, гибридный")
    roles: list[str] | None = Field(default=None, description="Роли, например менеджер по продукту, тимлид, системный аналитик")
    skills: list[str] | None = Field(default=None, description="Навыки, например дизайн, Java, фронтенд")
    having: list[str] | None = Field(default=None, description="Кто уже в команде: имена, роли или навыки")
    looking_for: list[str] | None = Field(default=None, description="Кого приглашает в команду: роли или навыки")
    experience: list[str] | None = Field(default=None, description="Профессиональный опыт и пет-проекты")
    interests: list[str] | None = Field(default=None, description="Интересы, например финансы, путешествия, спорт")
    idea: str | None = Field(description="Описание идеи проекта")

class DistanceWeights:
    reactions = 0.5
    location_location = 0.5
    roles_roles = -1.0
    skills_skills = -1.0
    having_roles = -1.0
    having_skills = -1.0
    looking_for_roles = 1.0
    looking_for_skills = 1.0
    experience_experience = 0.5
    interests_interests = 1.0
    idea_idea = 1.0
