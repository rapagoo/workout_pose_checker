"""개발 환경과 패키징 환경에서 공통으로 사용하는 애플리케이션 경로."""

import sys
from pathlib import Path


MODEL_FILENAME = "yolo26n-pose.pt"


def get_application_root():
    """소스 실행 시 프로젝트 루트, EXE 실행 시 실행 파일 폴더를 반환한다."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


def get_model_path():
    """애플리케이션이 사용할 외부 YOLO Pose 모델 경로를 반환한다."""
    return get_application_root() / "models" / MODEL_FILENAME
