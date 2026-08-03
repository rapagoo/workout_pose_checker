"""운동 코드별 자세 분석기를 외부에 공개한다."""

from .pushup import PushupAnalyzer
from .squat import SquatAnalyzer

__all__ = [
    "PushupAnalyzer",
    "SquatAnalyzer",
]
