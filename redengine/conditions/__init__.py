from redengine.core.condition import PARSERS, CLS_CONDITIONS
from .task import *
from .scheduler import *
from .time import *
from .git import *
from .parameter import ParamExists, IsEnv
from redengine.core.condition import AlwaysFalse, AlwaysTrue, All, Any, Not

true = AlwaysTrue()
false = AlwaysFalse()


def _set_is_period_parsing():
    from redengine.core.time import PARSERS as _TIME_PARSERS
    
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