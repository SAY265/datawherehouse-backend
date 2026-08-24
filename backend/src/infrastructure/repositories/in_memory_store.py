"""In-memory storage fallback for local development and offline database resilience."""

from typing import Any

from src.domain.data_model.entities import DataModel
from src.domain.project.entities import Project
from src.domain.sandbox.sandbox import SandboxConfig
from src.domain.user.entities import User


class InMemoryStore:
    """Thread-safe in-memory cache/fallback store."""

    _instance: "InMemoryStore | None" = None

    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.projects: dict[str, Project] = {}
        self.data_models: dict[str, DataModel] = {}
        self.sandbox_configs: dict[str, SandboxConfig] = {}

    @classmethod
    def get_instance(cls) -> "InMemoryStore":
        if cls._instance is None:
            cls._instance = InMemoryStore()
        return cls._instance

    # --- User operations ---
    def get_user_by_id(self, user_id: Any) -> User | None:
        return self.users.get(str(user_id))

    def get_user_by_username(self, username: str) -> User | None:
        normalized = username.strip().lower()
        for u in self.users.values():
            if u.username == normalized:
                return u
        return None

    def get_user_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        for u in self.users.values():
            if u.email.value == normalized:
                return u
        return None

    def save_user(self, user: User) -> User:
        self.users[str(user.id)] = user
        return user

    # --- Project operations ---
    def get_project_by_id(self, project_id: Any) -> Project | None:
        return self.projects.get(str(project_id))

    def list_projects_by_user(self, user_id: Any) -> list[Project]:
        return [p for p in self.projects.values() if str(p.user_id) == str(user_id)]

    def save_project(self, project: Project) -> Project:
        self.projects[str(project.id)] = project
        return project

    def delete_project(self, project_id: Any) -> bool:
        return self.projects.pop(str(project_id), None) is not None

    # --- DataModel operations ---
    def get_data_model_by_id(self, dm_id: Any) -> DataModel | None:
        return self.data_models.get(str(dm_id))

    def get_data_model_by_project_id(self, project_id: Any) -> DataModel | None:
        for dm in self.data_models.values():
            if str(dm.project_id) == str(project_id):
                return dm
        return None

    def save_data_model(self, data_model: DataModel) -> DataModel:
        self.data_models[str(data_model.id)] = data_model
        return data_model

    def update_data_model_if_revision_matches(self, data_model: DataModel, base_revision: int) -> DataModel | None:
        current = self.get_data_model_by_id(data_model.id)
        if current is None or current.revision != base_revision:
            return None
        self.data_models[str(data_model.id)] = data_model
        return data_model

    def delete_data_model(self, dm_id: Any) -> bool:
        return self.data_models.pop(str(dm_id), None) is not None

    # --- SandboxConfig operations ---
    def get_sandbox_config_by_project_id(self, project_id: Any) -> SandboxConfig | None:
        for sc in self.sandbox_configs.values():
            if str(sc.project_id) == str(project_id):
                return sc
        return None

    def save_sandbox_config(self, sandbox_config: SandboxConfig) -> SandboxConfig:
        self.sandbox_configs[str(sandbox_config.id)] = sandbox_config
        return sandbox_config

    def delete_sandbox_config(self, sc_id: Any) -> bool:
        return self.sandbox_configs.pop(str(sc_id), None) is not None
