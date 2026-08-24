"""Registry extensible cho các LangChain chat model provider."""

from collections.abc import Callable
from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException


@dataclass(frozen=True, slots=True)
class ChatModelConfiguration:
    """Cấu hình provider-neutral cho một chat model."""

    provider: str
    model_name: str
    api_key: str
    base_url: str
    temperature: float
    max_tokens: int
    timeout_seconds: float


ProviderBuilder = Callable[[ChatModelConfiguration], BaseChatModel]


class ChatModelProviderRegistry:
    """Ánh xạ provider name sang builder mà không sửa Agent."""

    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}

    def register(self, provider: str, builder: ProviderBuilder) -> None:
        """Đăng ký hoặc thay builder của provider."""
        self._builders[provider.casefold()] = builder

    def build(self, configuration: ChatModelConfiguration) -> BaseChatModel:
        """Dựng model hoặc báo lỗi cấu hình provider."""
        builder = self._builders.get(configuration.provider.casefold())
        if builder is None:
            raise InfrastructureException(
                ErrorCode.LLM_ERROR,
                f"LLM provider '{configuration.provider}' chưa được đăng ký.",
            )
        return builder(configuration)


def create_default_provider_registry() -> ChatModelProviderRegistry:
    """Tạo registry có OpenAI, OpenAI-compatible và Google Gemini."""
    registry = ChatModelProviderRegistry()
    registry.register("openai", _build_openai)
    registry.register("openai_compatible", _build_openai)
    registry.register("google", _build_google)
    return registry


def _build_openai(configuration: ChatModelConfiguration) -> BaseChatModel:
    """Dựng OpenAI hoặc endpoint tương thích OpenAI."""
    options: dict[str, object] = {
        "model": configuration.model_name,
        "api_key": configuration.api_key or "local",
        "temperature": configuration.temperature,
        "max_tokens": configuration.max_tokens,
        "timeout": configuration.timeout_seconds,
        "max_retries": 0,
    }
    if configuration.base_url:
        options["base_url"] = configuration.base_url
    return ChatOpenAI(**options)


def _build_google(configuration: ChatModelConfiguration) -> BaseChatModel:
    """Dựng Gemini qua package LangChain chính thức."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise InfrastructureException(
            ErrorCode.LLM_ERROR,
            "Thiếu dependency langchain-google-genai cho provider Google.",
        ) from exc
    return ChatGoogleGenerativeAI(
        model=configuration.model_name,
        google_api_key=configuration.api_key,
        temperature=configuration.temperature,
        max_output_tokens=configuration.max_tokens,
        timeout=configuration.timeout_seconds,
        max_retries=0,
    )
