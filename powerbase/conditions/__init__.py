from powerbase.core.conditions import PARSERS
from .task import *
from .scheduler import *
from .time import *
from .git import *
from .parameter import ParamExists, IsEnv
from powerbase.core.conditions import AlwaysFalse, AlwaysTrue, All, Any, Not

true = AlwaysTrue()
false = AlwaysFalse()


def _set_is_period_parsing():
    from powerbase.core.time import PARSERS as _TIME_PARSERS
    
    from functools import partial

    def _get_is_period(period_constructor, *args, **kwargs):
        period = period_constructor(*args, **kwargs)
        return IsPeriod(period=period)

    PARSERS.update(
        {
            parsing: partial(_get_is_period, period_constructor=parser)
            for parsing, parser in _TIME_PARSERS.items()
        }
    )
_set_is_period_parsing()