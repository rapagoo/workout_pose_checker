# 포즈 평가 코드 가이드

이 문서는 UI 개발자가 포즈 평가 코드의 책임과 데이터 흐름을 빠르게 이해하고,
연동 중 문제가 생겼을 때 수정 위치를 찾을 수 있도록 작성했습니다.

## 전체 처리 흐름

```text
OpenCV BGR 프레임
    ↓
PoseService.analyze_frame()
    ↓ YOLO 포즈 추론
가장 큰 사람 한 명 선택
    ↓
SquatAnalyzer 또는 PushupAnalyzer
    ↓ 관절 각도와 반복 상태 계산
UI용 결과 딕셔너리
    ↓
화면의 관절·상태·횟수 표시
```

UI는 YOLO나 운동 판정기를 직접 호출하지 않고 `PoseService`만 사용합니다.
반환 데이터의 상세 형식은 [모델·UI 연동 규칙](model_ui_contract.md)을 참고합니다.

## 파일별 역할

### `src/workout_pose_checker/pose_service.py`

모델 코드의 진입점입니다.

- YOLO 모델을 한 번 로드하고 재사용합니다.
- 프레임에서 사람이 감지되지 않으면 `PERSON_NOT_FOUND` 결과를 만듭니다.
- 여러 사람이 있으면 바운딩 박스 면적이 가장 큰 한 사람만 선택합니다.
- 운동 코드에 따라 스쿼트 또는 팔굽혀펴기 분석기를 호출합니다.
- NumPy 관절 좌표를 UI에서 사용할 수 있는 딕셔너리 배열로 변환합니다.
- `reset()`으로 선택한 운동의 상태와 횟수를 초기화합니다.

UI에서 사용하는 기본 예시는 다음과 같습니다.

```python
from src.workout_pose_checker import PoseService

service = PoseService(model_path="models/yolo26n-pose.pt")
result = service.analyze_frame(frame, exercise="squat")
service.reset(exercise="squat")
```

`PoseService`는 프레임마다 만들지 말고 애플리케이션 시작 시 한 번 생성해야 합니다.
매 프레임 생성하면 모델이 반복 로드되어 화면이 느려집니다.

### `src/workout_pose_checker/pose_utils.py`

운동 분석기가 함께 사용하는 계산 함수가 있습니다.

- `calculate_angle()`: 세 관절 좌표로 가운데 관절의 각도를 계산합니다.
- `select_visible_side()`: 필수 관절 신뢰도가 더 높은 왼쪽 또는 오른쪽을 선택합니다.

한쪽 필수 관절 중 하나라도 신뢰도 기준보다 낮으면 그쪽의 대표 신뢰도가 낮아집니다.
양쪽 모두 기준을 통과하지 못하면 `None`을 반환합니다.

### `src/workout_pose_checker/analyzers/squat.py`

스쿼트의 엉덩이·무릎 각도와 엉덩이 깊이를 계산하고 반복 상태를 관리합니다.

```text
READY → GO_DOWN → GO_UP → SUCCESS
```

- 관절이 굽혀지기 시작하면 `GO_DOWN`
- 최저점 조건이 연속 3프레임 유지되면 `GO_UP`
- 최저점에 도달한 뒤 선 자세가 연속 3프레임 유지되면 성공 횟수 증가
- 필요한 관절이 보이지 않으면 `JOINTS_NOT_VISIBLE`

판정 임계값은 파일 위쪽의 `STANDING_*`, `START_*`, `BOTTOM_*`,
`CONFIRM_FRAMES` 상수에서 조정합니다.

### `src/workout_pose_checker/analyzers/pushup.py`

팔굽혀펴기의 팔꿈치 각도와 어깨-엉덩이-발목의 몸통 각도를 계산합니다.

```text
READY → GO_DOWN → GO_UP → SUCCESS
                 ↘ KEEP_BODY_STRAIGHT
```

- 팔꿈치가 굽혀지기 시작하면 `GO_DOWN`
- 아래 자세가 연속 3프레임 유지되면 `GO_UP`
- 아래 자세를 거친 뒤 위 자세가 연속 3프레임 유지되면 성공 횟수 증가
- 진행 중 몸통이 기준보다 굽으면 `KEEP_BODY_STRAIGHT`

판정 임계값은 파일 위쪽의 `TOP_*`, `START_*`, `BOTTOM_*`,
`STRAIGHT_BODY_ANGLE`, `CONFIRM_FRAMES` 상수에서 조정합니다.

### `src/workout_pose_checker/webcam_pose.py`

포즈 평가 기능을 독립적으로 실행해 보는 샘플 프로그램입니다.

- 웹캠에서 OpenCV 프레임을 읽습니다.
- `PoseService`에 프레임과 운동 코드를 전달합니다.
- 반환된 관절, 각도, 상태와 성공 횟수를 화면에 그립니다.
- `q` 또는 `Esc`로 종료합니다.

실제 UI는 이 파일을 그대로 호출하기보다 `PoseService` 호출 방식과 결과 표시
부분을 참고해 UI 이벤트 루프에 맞게 연결하면 됩니다.

### `tests/`

실제 웹캠이나 YOLO 모델 없이 핵심 로직을 확인하는 단위 테스트입니다.

- `test_pose_service.py`: 모델 결과 선택, 반환 형식, 초기화와 오류 처리
- `test_squat_analyzer.py`: 스쿼트 상태 전환과 성공 횟수
- `test_pushup_analyzer.py`: 팔굽혀펴기 상태 전환과 자세 안내

## UI 연동 시 주의사항

- 입력 프레임은 OpenCV의 BGR 배열을 그대로 전달합니다.
- 화면 미러링은 분석 전에 하지 말고 UI 출력 단계에서 적용합니다.
- 운동 선택이 바뀌거나 초기화 버튼을 누르면 해당 운동에 `reset()`을 호출합니다.
- `status`는 화면 문구가 아닌 코드이므로 UI에서 사용자용 문구로 변환합니다.
- `detected=False`여도 `JOINTS_NOT_VISIBLE`이면 일부 `keypoints`가 존재할 수 있습니다.
- 모델 파일 누락이나 잘못된 운동 코드는 결과의 `error`가 아닌 Python 예외입니다.

## 새 운동 추가 순서

1. `analyzers/`에 기존 분석기와 같은 결과 형식의 새 클래스를 만듭니다.
2. `analyzers/__init__.py`에서 새 클래스를 공개합니다.
3. `PoseService.__init__()`의 기본 `analyzers` 딕셔너리에 운동 코드를 등록합니다.
4. `webcam_pose.py`의 CLI `choices`와 화면 측정값 표시를 확장합니다.
5. 분석기 상태 전환 테스트와 서비스 등록 테스트를 추가합니다.
6. `model_ui_contract.md`에 운동 코드와 `metrics` 필드를 기록합니다.

## 검증 방법

Conda 환경을 활성화한 뒤 프로젝트 루트에서 실행합니다.

```powershell
conda activate yolo_pose
python -m unittest discover -s tests -v
python -m src.workout_pose_checker.webcam_pose --exercise squat
python -m src.workout_pose_checker.webcam_pose --exercise pushup
```

단위 테스트는 계산과 상태 전환을 확인하고, 웹캠 실행은 카메라 위치와 실제 자세에서
임계값이 적절한지 확인하는 용도입니다.
