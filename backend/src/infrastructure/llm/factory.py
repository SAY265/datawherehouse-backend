"""Factory khởi tạo LLM tập trung, tự động nhận diện cấu hình từ Settings."""

from typing import Any

from config import Settings, get_settings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from src.common.logging import get_logger

logger = get_logger(__name__)

OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
OPENAI_DEFAULT_PREFIXES = ("gpt-", "chatgpt-", "o1", "o3", "o4")


class LLMFactory:
    """Factory tập trung quản lý việc khởi tạo các instance Chat LLM.

    Tự động chuẩn hóa cấu hình từ biến môi trường (OpenAI, OpenRouter, Ollama/Local).
    """

    @classmethod
    def resolve_provider_config(
        cls,
        api_key: str,
        base_url: str,
        model_name: str,
    ) -> tuple[str, str]:
        """Chuẩn hóa Base URL và Model Name dựa theo API Key và provider."""
        resolved_base_url = base_url.strip().rstrip("/")
        if not resolved_base_url and api_key.lower().startswith("sk-or-v1-"):
            resolved_base_url = OPENROUTER_BASE_URL

        resolved_model_name = model_name.strip()
        is_openrouter = resolved_base_url.casefold() == OPENROUTER_BASE_URL.casefold()

        if is_openrouter and "/" not in resolved_model_name and resolved_model_name.startswith(OPENAI_DEFAULT_PREFIXES):
            resolved_model_name = f"openai/{resolved_model_name}"

        return resolved_base_url, resolved_model_name

    @classmethod
    def is_local_provider(cls, api_key: str, base_url: str) -> bool:
        """Kiểm tra xem cấu hình có phải là Local LLM (Ollama, LMStudio...) hay không."""
        norm_key = api_key.strip().lower()
        norm_url = base_url.strip().lower()
        return "localhost" in norm_url or "127.0.0.1" in norm_url or norm_key in ("ollama", "local", "lmstudio")

    @classmethod
    def is_api_key_valid(cls, api_key: str, base_url: str) -> bool:
        """Kiểm tra tính hợp lệ của API Key."""
        if cls.is_local_provider(api_key, base_url):
            return True
        norm_key = api_key.strip().lower()
        return bool(norm_key and not norm_key.startswith(("sk-placeholder", "sk-your-")))

    @classmethod
    def create_chat_model(
        cls,
        settings: Settings | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model_name: str | None = None,
        timeout: int = 30,
        max_retries: int = 1,
        **extra_options: Any,
    ) -> BaseChatModel | None:
        """Tạo ChatOpenAI instance dựa trên cấu hình tập trung.

        Trả về None nếu không có API key hợp lệ và không phải môi trường local.
        """
        app_settings: Settings = settings or get_settings()
        api_key = app_settings.openrouter_api_key.strip() or app_settings.openai_api_key.strip()
        base_url = app_settings.openai_base_url.strip()
        target_model = model_name or app_settings.model_name
        target_temp = temperature if temperature is not None else app_settings.llm_temperature
        target_max_tokens = max_tokens if max_tokens is not None else app_settings.max_tokens

        if not cls.is_api_key_valid(api_key, base_url):
            logger.warning("LLM API key chưa được cấu hình hoặc là placeholder.")
            return None

        effective_key = api_key if cls.is_api_key_valid(api_key, base_url) else "ollama"
        resolved_base_url, resolved_model = cls.resolve_provider_config(effective_key, base_url, target_model)

        model_options: dict[str, Any] = {
            "api_key": effective_key,
            "model": resolved_model,
            "temperature": target_temp,
            "max_tokens": target_max_tokens,
            "timeout": timeout,
            "max_retries": max_retries,
            **extra_options,
        }
        if resolved_base_url:
            model_options["base_url"] = resolved_base_url

        return ChatOpenAI(**model_options)
