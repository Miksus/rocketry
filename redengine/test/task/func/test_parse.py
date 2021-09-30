
import inspect
import sys
from textwrap import dedent

from redengine.parse import parse_task

def test_parse_from_package(session, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        sys.path.append(str(tmpdir))
        
        task_dir = tmpdir.mkdir("funcs_test_parse_pkg") # This should be unique so other test imports won't interfere
        task_dir.join("__init__.py")
        task_dir.join("mytask.py").write(dedent("""
        def do_stuff_1():
            pass
        def do_stuff_2():
            pass
        """))
        task = parse_task({"class": "FuncTask", "func": "funcs_test_parse_pkg.mytask:do_stuff_1"})
        assert inspect.isfunction(task.func)
        assert "do_stuff_1" == task.func.__name__
        assert "funcs_test_parse_pkg.mytask:do_stuff_1" == task.name

        task = parse_task({"class": "FuncTask", "func": "funcs_test_parse_pkg.mytask.do_stuff_2"})
        assert inspect.isfunction(task.func)
        assert "do_stuff_2" == task.func.__name__
        assert "funcs_test_parse_pkg.mytask:do_stuff_2" == task.name
