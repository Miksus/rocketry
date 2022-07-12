

class Interval:
    "Mimics pandas.Interval"

    def __init__(self, left, right, closed="right"):
        self.left = left
        self.right = right
        self.closed = closed


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