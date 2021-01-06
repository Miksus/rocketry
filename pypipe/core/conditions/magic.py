
# TODO: Delete. This seems not to be used

class ConditionContainer:
    "Wraps another condition"

    __magicmethod__ = None

    def flatten(self):
        conditions = []
        for attr in self._cond_attrs:
            conds = getattr(self, attr)

            conditions += conds
        return conditions

    def apply(self, func, **kwargs):
        "Apply the function to all subconditions"
        subconds = []
        for subcond in self.subconditions:
            if isinstance(subcond, ConditionContainer):
                subcond = subcond.apply(func, **kwargs)
            else:
                subcond = func(subcond, **kwargs)
            subconds.append(subcond)
        return type(self)(*subconds)
        
    def __getitem__(self, val):
        return self.subconditions[val]

class Any(BaseCondition, ConditionContainer):

    __magicmethod__ = "__or__"

    def __init__(self, *conditions):
        self.subconditions = []

        self_type = type(self)
        for cond in conditions:
            # Avoiding nesting (like Any(Any(...), ...) --> Any(...))
            conds = cond.subconditions if isinstance(cond, self_type) else [cond]
            self.subconditions += conds

    def __bool__(self):
        return any(self.subconditions)

    def __repr__(self):
        string = ' | '.join(map(repr, self.subconditions))
        return f'({string})'

    def estimate_timedelta(self, dt):
        # As any of the conditions must be
        # true, it is safe to wait for the
        # one closest 
        return min(
            cond.estimate_timedelta(dt)
            if hasattr("estimate_timedelta")
            else 0
            for cond in self.subconditions
        )

    @property
    def cycle(self):
        "Aggregate the TimePeriods the condition has"
        all_timeperiods = all(isinstance(cond, TimeCondition) for cond in self.subconditions)
        if all_timeperiods:
            # Can be determined
            return time.Any(*[cond.cycle for cond in self.subconditions])
        else:
            # Cannot be determined --> all times may be valid
            return time.StaticInterval()

class All(BaseCondition, ConditionContainer):

    __magicmethod__ = "__or__"

    def __init__(self, *conditions):
        self.subconditions = []

        self_type = type(self)
        for cond in conditions:
            # Avoiding nesting (like All(All(...), ...) --> All(...))
            conds = cond.subconditions if isinstance(cond, self_type) else [cond]
            self.subconditions += conds

    def __bool__(self):
        return all(self.subconditions)

    def __repr__(self):
        string = ' & '.join(map(repr, self.subconditions))
        return f'({string})'

    def estimate_timedelta(self, dt):
        # As all of the conditions must be
        # true, it is safe to wait for the
        # one furthest away 
        return max(
            cond.estimate_timedelta(dt)
            if hasattr(cond, "estimate_timedelta")
            else datetime.timedelta.resolution
            for cond in self.subconditions
        )

    def __getitem__(self, val):
        return self.subconditions[val]

    @property
    def cycle(self):
        "Aggregate the TimePeriods the condition has"
        return time.All(*[cond.cycle for cond in self.subconditions])

class Not(BaseCondition, ConditionContainer):

    __magicmethod__ = "__invert__"

    def __init__(self, condition):
        self.condition = condition

    def __bool__(self):
        return not(self.condition)

    def __repr__(self):
        string = repr(self.condition)
        return f'~{string}'

    @property
    def subconditions(self):
        return (self.condition,)

    @property
    def cycle(self):
        "Aggregate the TimePeriods the condition has"
        if isinstance(self.condition, TimeCondition):
            # Can be determined
            return ~self.condition.cycle
        else:
            # Cannot be determined --> all times may be valid
            return time.StaticInterval()

    def __getattr__(self, name):
        """Called as last resort so the actual 
        condition's attribute returned to be more
        flexible"""
        return getattr(self.condition, name)

    def __invert__(self):
        "inverse of inverse is the actual condition"
        return self.condition