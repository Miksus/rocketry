import datetime

from rocketry.core.time.base import (
    All, Any
)
from rocketry.time import TimeOfDay, TimeOfMinute, always

from_iso = datetime.datetime.fromisoformat

def test_compress_any():
    assert Any(
        TimeOfDay(),
        TimeOfDay(),
        Any(TimeOfMinute(), TimeOfMinute()), # This is unnested
        All(TimeOfDay(), TimeOfMinute()),
    ) == Any(
        TimeOfDay(),
        TimeOfDay(),
        TimeOfMinute(), TimeOfMinute(), # This was unnested
        All(TimeOfDay(), TimeOfMinute()),
    )

    assert Any(
        TimeOfDay(),
        All(TimeOfDay(), TimeOfMinute()),
        always, # The other periods does not matter
        Any(TimeOfMinute(), TimeOfMinute()),
    ) == Any(always)


def test_compress_all():
    assert All(
        TimeOfDay(),
        TimeOfDay(),
        All(TimeOfMinute(), TimeOfMinute()), # This is unnested
        Any(TimeOfDay(), TimeOfMinute()),
    ) == All(
        TimeOfDay(),
        TimeOfDay(),
        TimeOfMinute(), TimeOfMinute(), # This was unnested
        Any(TimeOfDay(), TimeOfMinute()),
    )

    assert All(
        TimeOfDay(),
        All(TimeOfDay(), TimeOfMinute()),
        always, # This has no effect
        Any(TimeOfMinute(), TimeOfMinute()),
    ) == All(
        TimeOfDay(),
        All(TimeOfDay(), TimeOfMinute()),
        Any(TimeOfMinute(), TimeOfMinute()),
    )
