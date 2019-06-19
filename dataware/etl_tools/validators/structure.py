
class ValidatorBase:

    def validate(self, df):
        if hasattr(self, "checks"):
            for check in self.checks:
                is_ok = check["func"](df)
                if not is_ok:
                    msg = check.get("error msg", f"Failed on {check["func"].__name__}")
                    raise checks.get("exception", ETLError)(msg)
        else:
            raise NotImplementedError

    def add_check(self, check_func, error_message=None, exception=None):

        if error_message is None:
            error_message = f"Failed on {check_func.__name__}"

        self.checks.append(
            dict(
                "func": check_func,
                "error msg": error_message,
                "exception": exception
            )
        )


class _AxisValidator(ValidatorBase):

    def __init__(self, _attr, identical=None, 
                has_all=None, is_in=None, has_any=None, 
                has_not_any=None, dtype=None, length=None,
                min_value=None, max_value=None, 
                min_count=None, max_count=None):

        checks = []
        attr_name = _attr.capitalize()

        if identical:
            self.add_check(
                lambda df: (getattr(df, _attr) == identical).all(),
                f"{attr_name} not identical with {identical}"
            )

        if has_all:
            self.add_check(
                lambda df: all(col in getattr(df, _attr) for col in has_all),
                f"{attr_name} do not have all: {has_all}"
            )

        if is_in:
            self.add_check(
                lambda df: getattr(df, _attr).isin(is_in).all(),
                f"{attr_name} is not in: {is_in}"
            )

        if has_any:
            self.add_check(
                lambda df: any(col in getattr(df, _attr) for col in has_any),
                f"{attr_name} not have any of: {has_any}"
            )
        
        if has_not_any:
            self.add_check(
                lambda df: all(col not in getattr(df, _attr) in for col in has_not_any),
                f"{attr_name} have any of: {has_not_any}"
            )

        if dtype:
            self.add_check(
                lambda df: getattr(df, _attr).dtype == dtype,
                f"{attr_name} not type: {dtype}",
            )

        if length:
            self.add_check(
                lambda df: len(getattr(df, _attr)) == len(length),
                f"{attr_name} not in length: {length}"
            )

        if min_value:
            self.add_check(
                lambda df: (getattr(df, _attr) >= min_value).all(),
                f"{attr_name} has value less than: {min_value}"
            )
        if max_value:
            self.add_check(
                lambda df: (getattr(df, _attr) <= max_value).all(),
                f"{attr_name} has value greater than: {max_value}"
            )

        if min_count:
            self.add_check(
                lambda df: (len(getattr(df, _attr)) >= min_count).all(),
                f"{attr_name} has less values than: {min_count}"
            )
        if max_count:
            self.add_check(
                lambda df: (len(getattr(df, _attr)) <= max_count).all(),
                f"{attr_name} has more values than: {max_count}"
            )

        if hasattr(self, "checks"):
            self.checks += checks
        else:
            self.checks = checks

class ColumnValidator(ValidatorBase, _AxisValidator):
    
    def __init__(self, **kwargs):
        super().__init__(_attr="columns", **kwargs)


class IndexValdidator(ValidatorBase, _AxisValidator):

    def __init__(self, **kwargs):
        super().__init__(_attr="index", **kwargs)

class ValueValidator(ValidatorBase):

    def __init__(self, has_only_dtypes=None):

        if has_only_dtypes:
            self.add_check(
                lambda df: df.dtypes.isin(has_only_dtypes).all()
                            if isinstance(df, pd.DataFrame)
                            else df.dtype == has_only_dtypes,
                f"Dtype can only be {has_only_dtypes}"
            )

class DataValidator():

    def __init__(self, check_has_data=True, 
                        check_is_frame=False, check_is_series=False, 
                        min_column_count=None, max_column_count=None, 
                        min_row_count=None, max_row_count=None,
                        min_memory_usage=None, max_memory_usage=None):

        if check_has_data:
            self.add_check(
                lambda df: not df.empty,
                f"Has no data"
            )

        if check_is_frame:
            self.add_check(
                lambda df: not isinstance(df, pd.DataFrame),
                f"Is not DataFrame"
            )

        if check_is_series:
            self.add_check(
                lambda df: not isinstance(df, pd.Series),
                f"Is not Series"
            )

        if min_column_count:
            self.add_check(
                lambda df: len(df.columns) >= min_column_count
                f"Too few columns"
            )
        if max_column_count:
            self.add_check(
                lambda df: len(df.columns) <= max_column_count
                f"Too many columns"
            )

        if min_row_count:
            self.add_check(
                lambda df: len(df.index) >= min_row_count
                f"Too few rows"
            )
        if max_row_count:
            self.add_check(
                lambda df: len(df.index) <= max_row_count
                f"Too many rows"
            )

        if min_memory_usage:
            self.add_check(
                lambda df: df.memory_usage(index=True, deep=True).sum() 
                            if isinstance(df, pd.DataFrame) 
                            else df.memory_usage(index=True, deep=True) 
                            >= min_memory_usage,
                f"Size in memory unexpectedly low"
            )
        if max_memory_usage:
            self.add_check(
                lambda df: df.memory_usage(index=True, deep=True).sum() 
                            if isinstance(df, pd.DataFrame) 
                            else df.memory_usage(index=True, deep=True) 
                            <= max_memory_usage,
                f"Size in memory too high"
            )
