from pathlib import Path

def create_file(file, content):
    path = Path(file)
    path.parent.mkdir(exist_ok=True)
    #with open(path, "w") as f:
    #    f.write(content)
    path.write_text(content, encoding="utf-8")

def delete_file(file):
    Path(file).unlink()
