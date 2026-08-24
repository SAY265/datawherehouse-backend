"""Fallback executor invoking ~14B models (Local Ollama / Free Tier) when primary API key runs out."""

import os
from typing import Any
from langchain_openai import ChatOpenAI
from src.common.logging import get_logger

logger = get_logger(__name__)

DEFAULT_14B_MODEL = "qwen2.5-coder:14b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"
OPENROUTER_FREE_14B = "qwen/qwen-2.5-coder-32b-instruct:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_fallback_14b_models() -> list[dict[str, Any]]:
    """Trả về danh sách các model 14B dự phòng theo thứ tự ưu tiên (Local Ollama 14B -> Free Tier)."""
    try:
        from config import get_settings
        settings = get_settings()
        fallback_model = (os.getenv("FALLBACK_MODEL_NAME") or getattr(settings, "fallback_model_name", None) or DEFAULT_14B_MODEL).strip()
        fallback_url = (os.getenv("FALLBACK_BASE_URL") or getattr(settings, "fallback_base_url", None) or DEFAULT_OLLAMA_URL).strip()
        raw_key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY") or getattr(settings, "openrouter_api_key", None) or getattr(settings, "openai_api_key", None) or "").strip()
    except Exception:
        fallback_model = os.getenv("FALLBACK_MODEL_NAME", DEFAULT_14B_MODEL).strip() or DEFAULT_14B_MODEL
        fallback_url = os.getenv("FALLBACK_BASE_URL", DEFAULT_OLLAMA_URL).strip() or DEFAULT_OLLAMA_URL
        raw_key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY") or "").strip()

    openrouter_key = raw_key if (raw_key and not raw_key.lower().startswith(("sk-placeholder", "sk-your-"))) else "none"

    candidates = [
        # 1. Local Ollama 14B (chạy offline trực tiếp trên máy, không phụ thuộc API key)
        {
            "name": f"Local Ollama ({fallback_model})",
            "model": fallback_model,
            "base_url": fallback_url,
            "api_key": "ollama",
            "temperature": 0.1,
            "max_tokens": 1500,
            "timeout": 3,
        },
        # 2. OpenRouter Free Tier (Model 14B-32B miễn phí nếu có kết nối mạng)
        {
            "name": f"OpenRouter Free Tier ({OPENROUTER_FREE_14B})",
            "model": OPENROUTER_FREE_14B,
            "base_url": OPENROUTER_BASE_URL,
            "api_key": openrouter_key,
            "temperature": 0.1,
            "max_tokens": 1500,
            "timeout": 5,
        },
    ]
    return candidates


async def invoke_with_14b_fallback(
    messages: list[Any],
    structured_schema: Any = None,
    timeout: float = 60.0,
) -> Any:
    """Thử lần lượt các model 14B dự phòng khi API key chính bị hết credit hoặc lỗi."""
    import asyncio

    candidates = get_fallback_14b_models()
    last_err: Exception | None = None

    for candidate in candidates:
        try:
            logger.info("Đang kích hoạt Model dự phòng 14B: %s...", candidate["name"])
            model = ChatOpenAI(
                model=candidate["model"],
                base_url=candidate["base_url"],
                api_key=candidate["api_key"],
                temperature=candidate["temperature"],
                max_tokens=candidate["max_tokens"],
                timeout=candidate["timeout"],
                max_retries=1,
            )
            if structured_schema:
                try:
                    runnable = model.with_structured_output(structured_schema, method="json_mode")
                    response = await asyncio.wait_for(runnable.ainvoke(messages), timeout=timeout)
                except Exception:
                    runnable = model.with_structured_output(structured_schema)
                    response = await asyncio.wait_for(runnable.ainvoke(messages), timeout=timeout)
            else:
                response = await asyncio.wait_for(model.ainvoke(messages), timeout=timeout)

            logger.info("Model dự phòng 14B (%s) phản hồi thành công!", candidate["name"])
            return response
        except Exception as exc:
            last_err = exc
            logger.warning("Model dự phòng 14B (%s) không khả dụng: %s", candidate["name"], exc)

    if last_err:
        raise last_err
    raise RuntimeError("Tất cả các model 14B dự phòng đều không thể phản hồi.")
