from dataclasses import dataclass
from typing import Any

try:
    from typing import Literal
except ImportError: # pragma: no cover
    from typing_extensions import Literal

@dataclass(frozen=True)
class Interval:
    "Mimics pandas.Interval"

    left: Any
    right: Any
    closed: Literal['left', 'right', 'both', 'neither'] = "left"

    def __post_init__(self):
        if self.left > self.right:
            raise ValueError("Left cannot be greater than right")

        if self.closed not in ('left', 'right', 'both', 'neither'):
            raise ValueError(f"Invalid close: {self.closed}")


    def __contains__(self, dt):
        if self.closed == "right":
            return self.left < dt <= self.right
        if self.closed == "left":
            return self.left <= dt < self.right
        if self.closed == "both":
            return self.left <= dt <= self.right
        return self.left < dt < self.right

    def overlaps(self, other:'Interval'):
        # Simple case: No overlap if:

        # self:  |------|
        # other:          |------|
        is_self_on_far_left = self.right < other.left

        # Or:
        # self:           |------|
        # other: |------|
        is_self_on_far_right = self.left > other.right
        is_not_overlap = is_self_on_far_left or is_self_on_far_right
        if is_not_overlap:
            return False

        # More complex:
        # self:  |------?
        # other:        ?------|
        if self.right == other.left:
            if self.closed in ('left', 'neither') or other.closed in ('right', 'neither'):
                # self:  |------*
                # other:        |------|

                # self:  |------|
                # other:        *------|
                return False

        # self:         ?------|
        # other: |------?
        if self.left == other.right:
            if self.closed in ('right', 'neither') or other.closed in ('left', 'neither'):
                # self:         *------|
                # other: |------|

                # self:         |------|
                # other: |------*
                return False

        return True

    def __and__(self, other):
        "Find interval that both overlaps"

        if self.left > other.left:
            left = self.left
            left_closed = self.closed in ('left', 'both')
        elif self.left < other.left:
            left = other.left
            left_closed = other.closed in ('left', 'both')
        else:
            # Equal
            left = self.left
            left_closed = self.closed in ('left', 'both') and other.closed in ('left', 'both')

        if self.right < other.right:
            right = self.right
            right_closed = self.closed in ('right', 'both')
        elif self.right > other.right:
            right = other.right
            right_closed = other.closed in ('right', 'both')
        else:
            # Equal
            right = self.right
            right_closed = self.closed in ('right', 'both') and other.closed in ('right', 'both')

        closed = (
            "both" if left_closed and right_closed
            else 'left' if left_closed
            else 'right' if right_closed
            else 'neither'
        )

        return Interval(left, right, closed=closed)

    @property
    def is_empty(self):
        "Check if constains no points"
        if self.closed == "both":
            has_points = self.left <= self.right
        elif self.closed in ('left', 'right', 'neither'):
            has_points = self.left < self.right

        return not has_points

    def __repr__(self):
        return f'Interval({repr(self.left)}, {repr(self.right)}, closed={repr(self.closed)})'
