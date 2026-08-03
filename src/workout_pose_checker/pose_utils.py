"""운동 분석기에서 공통으로 사용하는 관절 계산 도우미."""

import math


def calculate_angle(point_a, point_b, point_c):
    """세 점으로 point_b를 꼭짓점으로 하는 0~180도 사이의 각도를 계산한다."""
    vector_ba = (
        point_a[0] - point_b[0],
        point_a[1] - point_b[1],
    )
    vector_bc = (
        point_c[0] - point_b[0],
        point_c[1] - point_b[1],
    )

    cross = (
        vector_ba[0] * vector_bc[1]
        - vector_ba[1] * vector_bc[0]
    )
    dot = (
        vector_ba[0] * vector_bc[0]
        + vector_ba[1] * vector_bc[1]
    )

    return math.degrees(math.atan2(abs(cross), dot))


def select_visible_side(
    scores,
    side_indexes,
    min_confidence=0.5,
):
    """필수 관절 신뢰도가 더 높은 신체 좌우 측을 선택한다."""
    # 한쪽 관절 중 가장 낮은 신뢰도를 그 측면의 대표 신뢰도로 사용한다.
    side_scores = {
        side: min(scores[index] for index in indexes)
        for side, indexes in side_indexes.items()
    }

    selected_side = max(side_scores, key=side_scores.get)

    # 가장 잘 보이는 쪽도 기준 미만이면 분석할 수 없는 프레임이다.
    if side_scores[selected_side] < min_confidence:
        return None

    return selected_side
