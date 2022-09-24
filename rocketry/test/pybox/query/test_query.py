
import datetime
import pytest
from rocketry.pybox import query

@pytest.mark.parametrize('qry,data,expected',
    [
        pytest.param(
            query.Key('mykey') == 10,
            [
                {'mykey': 5},
                {'mykey': 10},
                {'mykey': 11},
            ],
            [{'mykey': 10}],
            id="equal"
        ),
        pytest.param(
            query.Key('mydate') == '2021-01-01',
            [
                {'mydate': datetime.datetime.fromisoformat('2020-12-31')},
                {'mydate': datetime.datetime.fromisoformat('2021-01-01')},
                {'mydate': datetime.datetime.fromisoformat('2020-01-02')},
            ],
            [{'mydate': datetime.datetime.fromisoformat('2021-01-01')}],
            id="string to datetime"
        ),
    ]
)
def test_filter(qry, data, expected):
    assert list(qry.filter(data)) == expected
