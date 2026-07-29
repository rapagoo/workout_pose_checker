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

- 운동 코드: `"squat"` 또는 `"pushup"`
- 모델 입력에는 회전과 좌우 반전을 적용하지 않습니다.
- 화면 좌우 반전은 UI 출력 단계에서 적용합니다.
- `L`과 `R`은 운동하는 사람의 신체 기준입니다.

## 반환 형식

```python
{
    "detected": True,
    "exercise": "squat",
    "status": "BOTTOM",
    "success_count": 3,
    "failure_count": 1,
    "side": "L",
    "metrics": {
        "hip_angle": 92.4,
        "knee_angle": 104.8,
        "hip_depth": -0.12,
    },
    "keypoints": [],
    "error": None,
}
```

상태 코드는 다음 값을 사용합니다.

```text
READY
MOVING
BOTTOM
UP
DOWN
SUCCESS
FAIL
PERSON_NOT_FOUND
JOINTS_NOT_VISIBLE
```

모델은 상태 코드를 반환하고, UI가 이를 사용자용 문구로 변환합니다.

## 초기화

운동 변경 또는 초기화 버튼 입력 시 UI가 다음 메서드를 호출합니다.

```python
pose_service.reset(exercise="squat")
```
