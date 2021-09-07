
from redengine.cli import main
from pathlib import Path

def test_create(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        assert not Path("myproject").is_dir()

        main(["create", "myproject"])
        assert Path("myproject").is_dir()
        assert Path("myproject/tasks").is_dir()
        assert Path("myproject/main.py").is_file()