import enum


class AssetStatus(str, enum.Enum):
    """자산 상태"""

    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class InterpType(str, enum.Enum):
    """보간 방식"""

    STEP = "STEP"
    LINEAR = "LINEAR"

