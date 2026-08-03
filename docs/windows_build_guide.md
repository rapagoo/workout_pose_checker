# Windows 실행 파일 빌드 가이드

Workout Pose Checker를 PyInstaller 기반 Windows 실행 파일로 만드는 방법을
설명합니다. 빌드 결과는 실행 파일 하나가 아니라 필요한 라이브러리를 포함한
폴더 형태로 생성됩니다.

## 1. 사전 준비

### Conda 환경 활성화

Anaconda Prompt에서 프로젝트 루트로 이동한 뒤 `yolo_pose` 환경을 활성화합니다.

```powershell
conda activate yolo_pose
```

환경을 새로 구성하거나 기준 파일에 맞춰 갱신해야 한다면 다음 명령을 사용합니다.

```powershell
conda env create -f environment.yml

# 기존 환경 갱신
conda env update -n yolo_pose -f environment.yml --prune
```

PyInstaller 설치 여부는 다음 명령으로 확인합니다.

```powershell
python -m PyInstaller --version
```

### 모델 파일 확인

다음 위치에 YOLO Pose 모델이 있어야 합니다.

```text
models/yolo26n-pose.pt
```

모델 파일은 Git에서 제외되므로 새 PC에서는 별도로 준비해야 합니다.

## 2. 빌드 전 설정

`src/workout_pose_checker/main_window.py`에서 배포 목적에 맞게 스위치를
설정합니다.

일반 배포용 권장 설정:

```python
USE_MOCK_POSE_SERVICE = False
SHOW_POSE_LANDMARKS = False
```

관절점과 연결선을 확인하는 디버그 빌드에서는 다음 값을 사용합니다.

```python
SHOW_POSE_LANDMARKS = True
```

설정을 변경했다면 실행 파일을 다시 빌드해야 반영됩니다.

## 3. 실행 파일 빌드

프로젝트 루트에서 제공된 PowerShell 스크립트를 실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

스크립트는 다음 작업을 자동으로 수행합니다.

1. `WorkoutPoseChecker.spec`을 이용하여 PyInstaller 빌드
2. 기존 PyInstaller 캐시와 중간 결과 정리
3. `dist/WorkoutPoseChecker/` 배포 폴더 생성
4. 모델 파일을 배포 폴더의 `models/`에 복사

Torch와 Ultralytics 의존성을 분석하므로 첫 빌드에는 몇 분이 걸릴 수 있습니다.

## 4. 빌드 결과 실행

올바른 실행 파일은 다음 위치에 있습니다.

```text
dist/WorkoutPoseChecker/WorkoutPoseChecker.exe
```

최종 배포 폴더의 기본 구조는 다음과 같습니다.

```text
dist/WorkoutPoseChecker/
├─ WorkoutPoseChecker.exe
├─ models/
│  └─ yolo26n-pose.pt
└─ _internal/
   └─ Python, Qt, Torch 및 기타 실행 라이브러리
```

`build/WorkoutPoseChecker/WorkoutPoseChecker.exe`는 PyInstaller가 빌드 과정에서
만드는 중간 파일입니다. 이 파일을 실행하면 `python310.dll` 등의 라이브러리를
찾지 못할 수 있으므로 사용하지 않습니다.

## 5. 배포 방법

`WorkoutPoseChecker.exe`만 따로 복사하면 프로그램이 실행되지 않습니다.
다음 폴더 전체를 하나의 배포 단위로 사용해야 합니다.

```text
dist/WorkoutPoseChecker/
```

다른 PC에 전달할 때는 이 폴더 전체를 ZIP으로 압축하여 전달합니다. 압축을 푼
뒤에도 EXE와 `_internal`, `models` 폴더의 상대 위치가 유지되어야 합니다.

현재 GPU용 Torch와 CUDA 라이브러리가 포함되므로 전체 산출물 크기가 약 3GB를
넘을 수 있습니다. GPU 지원이 필요 없는 배포본은 별도의 CPU 전용 Torch 환경에서
빌드해야 크기를 크게 줄일 수 있습니다.

## 6. 빌드 결과 확인

실행 파일을 연 뒤 다음 항목을 확인합니다.

- 운동 선택 이미지가 표시되는지
- YOLO 모델이 오류 없이 로드되는지
- 웹캠 영상이 표시되는지
- 스쿼트와 팔굽혀펴기가 정상적으로 분석되는지
- 관절 표시 스위치가 빌드 설정대로 적용되는지
- 목표 달성 후 결과 화면으로 이동하는지
- 운동 포기와 프로그램 종료 후 카메라가 해제되는지

Windows에서 카메라 권한을 요청하면 접근을 허용해야 합니다.

## 7. 자주 발생하는 문제

### Failed to load Python DLL

오류 예시:

```text
Failed to load Python DLL ... python310.dll
```

다음 두 가지를 확인합니다.

1. `build/`가 아니라 `dist/WorkoutPoseChecker/`의 EXE를 실행했는지
2. EXE만 따로 복사하지 않고 `_internal/` 폴더와 함께 실행했는지

### 모델 파일을 찾을 수 없음

다음 위치에 모델 파일이 있는지 확인합니다.

```text
dist/WorkoutPoseChecker/models/yolo26n-pose.pt
```

없다면 빌드 스크립트를 다시 실행하거나 원본 모델을 위 위치로 복사합니다.

### 빌드 명령에서 PyInstaller를 찾지 못함

`yolo_pose` 환경이 활성화되어 있는지 확인한 뒤 다음 명령으로 설치합니다.

```powershell
python -m pip install pyinstaller
```

### 실행 직후 아무 화면 없이 종료됨

`WorkoutPoseChecker.spec`에서 다음 값을 임시로 변경하여 콘솔이 표시되는 디버그
빌드를 만듭니다.

```python
console=True
```

다시 빌드한 뒤 콘솔에 출력되는 오류 메시지를 확인합니다. 문제를 해결한 후에는
일반 GUI 배포를 위해 `console=False`로 되돌립니다.

## 8. Git 관리

빌드 중간 파일과 최종 산출물은 `.gitignore`에 의해 Git에서 제외됩니다.

```gitignore
/build/
/dist/
```

다음 재현용 파일은 Git에 포함합니다.

- `WorkoutPoseChecker.spec`
- `scripts/build_windows.ps1`
- `docs/windows_build_guide.md`

모델 가중치와 실행 파일 산출물은 Git에 커밋하지 않습니다.
