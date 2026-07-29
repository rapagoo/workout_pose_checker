import math


def calculate_angle(point_a, point_b, point_c):
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
    side_scores = {
        side: min(scores[index] for index in indexes)
        for side, indexes in side_indexes.items()
    }

    selected_side = max(side_scores, key=side_scores.get)

    if side_scores[selected_side] < min_confidence:
        return None

    return selected_side