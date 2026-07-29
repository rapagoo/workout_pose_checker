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

- 현재 지원 운동 코드: `"squat"`
- `"pushup"`은 추후 지원 예정입니다.
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
    "failure_count": 0,
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
| `PERSON_NOT_FOUND` | 사람이 감지되지 않은 상태 | 화면 안으로 들어와 주세요 |
| `JOINTS_NOT_VISIBLE` | 판정에 필요한 관절이 충분히 보이지 않는 상태 | 자세가 잘 보이도록 위치를 조정해 주세요 |

충분히 내려가지 않고 시작 자세로 돌아오면 실패로 기록하지 않고
`READY`로 복귀합니다. `failure_count`는 기존 UI 호환성을 위해 유지하며
현재는 항상 `0`입니다.

모델은 상태 코드를 반환하고, UI가 이를 사용자용 문구로 변환합니다.

모델 파일 누락, 지원하지 않는 운동 코드, 추론 실패 등의 오류는
결과 딕셔너리의 `error`가 아니라 Python 예외로 전달됩니다.
현재 `error` 필드는 호환성을 위해 유지하며 정상 반환에서는 `None`입니다.

## 초기화

운동 변경 또는 초기화 버튼 입력 시 UI가 다음 메서드를 호출합니다.

```python
pose_service.reset(exercise="squat")
```
