
from textwrap import dedent
import pytest
from redengine.args import YamlArg

def test_construct(tmpdir):
    pytest.importorskip("yaml")
    fh = tmpdir.join("arg.yaml")
    fh.write(dedent("""
    myfield:
        innerfield: 'a value'
    """))
    file = str(fh)
    arg = YamlArg(file, field=['myfield', 'innerfield'])
    assert 'a value' == arg.get_value()