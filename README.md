# Workout Pose Checker

YOLO26 Pose를 이용해 스쿼트와 팔굽혀펴기 자세를 분석하는 2인 단기 프로젝트입니다.
현재 단계에서는 웹캠 포즈 추론부터 검증합니다.

## 확인된 개발 환경

- Python 3.10.20
- Ultralytics 8.4.109
- PyTorch 2.13.0 (현재 PC는 CPU 전용 빌드)
- OpenCV 5.0.0.93
- Conda 환경 이름: `yolo_pose`

`environment.yml`은 새 환경을 만들기 위한 팀 기준 파일이고,
`requirements-lock.txt`는 2026-07-29에 설치되어 있던 전체 패키지 스냅샷입니다.
가상환경 폴더 자체는 공유하지 않습니다.

## 환경 만들기

Anaconda Prompt에서 프로젝트 폴더로 이동한 후 실행합니다.

```powershell
conda env create -f environment.yml
conda activate yolo_pose
python --version
```

기존 환경을 팀 기준 파일에 맞춰 갱신할 때는 다음 명령을 사용합니다.

```powershell
conda env update -n yolo_pose -f environment.yml --prune
```

GPU를 사용하는 PC는 먼저 위 환경을 만든 다음, 해당 PC의 NVIDIA 드라이버에
맞는 PyTorch 빌드로 교체합니다. GPU 빌드는 컴퓨터마다 다를 수 있으므로
`environment.yml`에 CUDA 구성을 강제로 고정하지 않습니다.

## 실행

`yolo26n-pose.pt`를 `models/`에 넣고 프로젝트 루트에서 실행합니다.

```powershell
python -m src.workout_pose_checker.webcam_pose
```

스쿼트 또는 팔굽혀펴기를 지정해서 실행할 수 있습니다.

```powershell
python -m src.workout_pose_checker.webcam_pose --exercise squat
python -m src.workout_pose_checker.webcam_pose --exercise pushup
```

팔굽혀펴기는 어깨, 팔꿈치, 손목, 엉덩이, 발목이 보이도록
카메라를 몸의 측면에 놓아야 안정적으로 판정됩니다.

모델 가중치, 데이터셋, `runs/` 결과물은 Git에 올리지 않습니다.
팀원 간에는 공유 드라이브나 릴리스 자산 등 별도 저장소로 전달합니다.

## 폴더 구조

```text
data/                       로컬 데이터셋 (Git 제외)
models/                     모델 가중치 (Git 제외)
runs/                       Ultralytics 실행 결과 (Git 제외)
src/workout_pose_checker/   애플리케이션 코드
tests/                      테스트
environment.yml             팀 환경 기준
requirements-lock.txt       현재 설치 상태 스냅샷
```

## 개발 문서

- [포즈 평가 코드 가이드](docs/pose_evaluation_guide.md): 파일별 역할, 처리 흐름,
  상태 판정 방식과 기능 확장 방법
- [모델·UI 연동 규칙](docs/model_ui_contract.md): UI 호출 방법과 반환 데이터 계약

## Git 브랜치 운영

두 명이 짧게 진행하므로 Git Flow 대신 단순한 GitHub Flow를 사용합니다.

- `main`: 언제든 실행 가능한 통합 브랜치. 직접 작업하지 않습니다.
- `feature/<작업>`: 기능별 단기 브랜치입니다.
- `fix/<작업>`: 버그 수정용 단기 브랜치입니다.

예시:

```text
feature/pose-landmarks
feature/squat-counter
feature/squat-feedback
fix/webcam-disconnect
```

작업 흐름:

```powershell
git switch main
git pull origin main
git switch -c feature/squat-counter

# 작업 및 커밋
git add <변경한 파일>
git commit -m "feat: add squat repetition counter"
git push -u origin feature/squat-counter
```

GitHub에서 `main` 대상 Pull Request를 열고 상대방이 확인한 뒤 squash merge합니다.
PR은 가능하면 하루 안에 합칠 수 있을 만큼 작게 유지합니다. 두 사람이 사람별
장기 브랜치를 하나씩 갖기보다는 기능별 브랜치를 만드는 편이 충돌과 통합 부담이
작습니다.

권장 GitHub 설정:

- `main` 브랜치 직접 push 금지
- Pull Request 승인 1명 필수
- merge 전 최신 `main` 반영
- squash merge 사용

