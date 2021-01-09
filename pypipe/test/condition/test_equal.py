
from pypipe.conditions import (
    AlwaysTrue, AlwaysFalse, 
    All, Any, Not,
    TaskFailed, TaskFinished, TaskRunning, TaskStarted, TaskSucceeded,
)
import pytest


@pytest.mark.parametrize(
    "get_cond",
    [
        pytest.param(lambda: AlwaysTrue(), id="AlwaysTrue"),
        pytest.param(lambda: AlwaysFalse(), id="AlwaysFalse"),
        pytest.param(lambda: All(AlwaysTrue(), AlwaysTrue()), id="All"),
        pytest.param(lambda: Any(AlwaysTrue(), AlwaysTrue()), id="Any"),
        pytest.param(lambda: Not(AlwaysTrue()), id="Not"),
        pytest.param(lambda: Not(Any(AlwaysTrue(), All(AlwaysTrue(), AlwaysTrue()))), id="Nested"),
    ],
)
def test_equal(get_cond):
    assert get_cond() == get_cond()
