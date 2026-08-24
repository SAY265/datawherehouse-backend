"""Adapter anonymize PII qua Microsoft Presidio Anonymizer."""

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, RecognizerResult
from presidio_anonymizer.entities.invalid_exception import InvalidParamError
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.security.pii.masking_policy import PiiMaskingPolicy
from src.infrastructure.security.pii.pii_detection import PiiDetection


class PresidioPiiAnonymizer:
    """Áp dụng masking policy lên các vùng PII đã phát hiện."""

    def __init__(self, engine: AnonymizerEngine) -> None:
        """Lưu anonymizer engine dùng chung giữa nhiều request."""
        self._engine = engine

    def anonymize(
        self,
        text: str,
        detections: tuple[PiiDetection, ...],
        policy: PiiMaskingPolicy,
    ) -> str:
        """Ẩn các vùng PII bằng operator được policy cấu hình.

        Raises:
            InfrastructureException: Khi Presidio anonymizer lỗi.
        """
        if not detections:
            return text
        try:
            result = self._engine.anonymize(
                text=text,
                analyzer_results=[_to_presidio(item) for item in detections],
                operators=_build_operators(policy),
            )
        except (InvalidParamError, TypeError, ValueError) as exc:
            raise InfrastructureException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="Không thể che thông tin cá nhân.",
            ) from exc
        return result.text


def _to_presidio(detection: PiiDetection) -> RecognizerResult:
    """Chuyển detection nội bộ sang input của Presidio Anonymizer."""
    return RecognizerResult(
        detection.entity_type,
        detection.start,
        detection.end,
        detection.score,
    )


def _build_operators(policy: PiiMaskingPolicy) -> dict[str, OperatorConfig]:
    """Chuyển masking policy sang operator map của Presidio."""
    return {
        entity: OperatorConfig(operator.name, dict(operator.parameters))
        for entity, operator in policy.operators.items()
    }
