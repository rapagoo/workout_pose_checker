# 모델·UI 연동 규칙

## 역할

- 모델: 포즈 추론, 관절 계산, 운동 판정, 횟수 관리
- UI: 웹캠 입력, 화면 표시, 운동 선택, 좌우 반전, 상태 문구 표시

## 호출 방법

UI는 원본 OpenCV BGR 프레임과 운동 코드를 전달합니다.

```python
result = pose_service.analyze_frame(
    frame=frame,
    exercise="squat",
)
```

- 현재 지원 운동 코드: `"squat"`, `"pushup"`
- 모델 입력에는 회전과 좌우 반전을 적용하지 않습니다.
- 화면 좌우 반전은 UI 출력 단계에서 적용합니다.
- `L`과 `R`은 운동하는 사람의 신체 기준입니다.
- 여러 사람이 감지되면 바운딩 박스 면적이 가장 큰 한 사람만 분석합니다.

## 반환 형식

```python
{
    "detected": True,
    "exercise": "squat",
    "status": "GO_UP",
    "success_count": 3,
    "side": "L",
    "metrics": {
        "hip_angle": 92.4,
        "knee_angle": 104.8,
        "hip_depth": -0.12,
    },
    "keypoints": [
        {
            "index": 0,
            "x": 321.5,
            "y": 108.2,
            "confidence": 0.93,
        },
    ],
    "error": None,
}
```

`keypoints`는 선택된 한 사람의 COCO 형식 관절 17개를 담습니다.

- `index`: COCO 관절 번호
- `x`, `y`: 원본 프레임 기준 픽셀 좌표
- `confidence`: 관절 신뢰도
- 사람이 감지되지 않으면 빈 배열

`detected`는 운동 분석에 필요한 관절이 충분히 감지됐는지를 나타냅니다.
`JOINTS_NOT_VISIBLE` 상태에서는 `false`이지만 `keypoints`는 존재할 수 있습니다.

상태 코드는 다음 값을 사용합니다.

```text
READY
GO_DOWN
GO_UP
SUCCESS
KEEP_BODY_STRAIGHT
PERSON_NOT_FOUND
JOINTS_NOT_VISIBLE
```

상태의 의미와 권장 UI 문구는 다음과 같습니다.

| 상태 | 의미 | 권장 UI 문구 |
| --- | --- | --- |
| `READY` | 시작 자세에서 운동을 준비하는 상태 | 준비 |
| `GO_DOWN` | 움직이기 시작했으며 충분한 깊이까지 내려가야 하는 상태 | 내려가세요 |
| `GO_UP` | 충분한 깊이에 도달하여 시작 자세로 올라와야 하는 상태 | 올라오세요 |
| `SUCCESS` | 정상적으로 1회를 완료한 상태 | 성공! |
| `KEEP_BODY_STRAIGHT` | 팔굽혀펴기 중 몸이 충분히 일직선이 아닌 상태 | 몸을 곧게 펴세요 |
| `PERSON_NOT_FOUND` | 사람이 감지되지 않은 상태 | 화면 안으로 들어와 주세요 |
| `JOINTS_NOT_VISIBLE` | 판정에 필요한 관절이 충분히 보이지 않는 상태 | 자세가 잘 보이도록 위치를 조정해 주세요 |

충분히 내려가지 않고 시작 자세로 돌아오면 횟수를 변경하지 않고
`READY`로 복귀합니다.

모델은 상태 코드를 반환하고, UI가 이를 사용자용 문구로 변환합니다.

모델 파일 누락, 지원하지 않는 운동 코드, 추론 실패 등의 오류는
결과 딕셔너리의 `error`가 아니라 Python 예외로 전달됩니다.
현재 `error` 필드는 호환성을 위해 유지하며 정상 반환에서는 `None`입니다.

## 초기화

운동 변경 또는 초기화 버튼 입력 시 UI가 다음 메서드를 호출합니다.

```python
pose_service.reset(exercise="squat")
```

## Mock 서비스로 UI 테스트

`MockPoseService`는 모델 가중치나 실제 운동 없이 UI의 상태 문구와 성공 횟수
표시를 확인하기 위한 테스트 서비스입니다. 실제 `PoseService`와 동일하게
`analyze_frame(frame, exercise)`와 `reset(exercise)`를 호출합니다.

UI의 서비스 생성 부분만 다음과 같이 교체합니다.

```python
from src.workout_pose_checker.mock_pose_service import MockPoseService

pose_service = MockPoseService(frames_per_status=30)
```

프레임을 처리하는 UI 코드는 실제 모델을 사용할 때와 같습니다.

```python
result = pose_service.analyze_frame(
    frame=frame,
    exercise=selected_exercise,
)
```

Mock 서비스는 입력 프레임의 내용을 분석하지 않고 다음 상태를 반복해서
반환합니다.

```text
READY → GO_DOWN → GO_UP → SUCCESS → READY
```

`frames_per_status`는 각 상태를 유지하는 프레임 수입니다. UI가 초당
약 30프레임으로 실행된다면 기본값 `30`은 상태당 약 1초에 해당합니다.
`SUCCESS`에 처음 진입할 때만 `success_count`가 1 증가합니다.

운동을 변경하거나 UI의 초기화 버튼을 누를 때는 반드시 초기화합니다.

```python
pose_service.reset(exercise=selected_exercise)
```

현재 Mock 서비스는 상태 문구와 성공 횟수 확인을 위한 최소 구현입니다.

- `detected`: 항상 `True`
- `side`: 항상 `None`
- `keypoints`: 항상 빈 배열이므로 스켈레톤을 표시하지 않음
- `metrics`: 운동별 키는 제공하지만 값은 모두 `None`
- 지원 운동: `"squat"`, `"pushup"`

따라서 UI는 Mock 모드에서 상태 문구, 성공 횟수, 운동 변경과 초기화 동작을
확인할 수 있습니다. 실제 관절 각도와 스켈레톤 표시는 실제 `PoseService`로
확인합니다.
