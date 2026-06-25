from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.8.1"


def test_version_alignment():
    assert (ROOT / "VERSION").read_text().strip() == VERSION
    assert f'version = "{VERSION}"' in (ROOT / "pyproject.toml").read_text()
    assert VERSION in (ROOT / "README.md").read_text()
    assert "Version: v1.8" in (
        ROOT / "src" / "pediatric_asthma_ventilation_simulator" / "asthma_engine.py"
    ).read_text()


def test_no_loose_compiled_artifacts():
    banned = []
    for path in ROOT.rglob("*.pyc"):
        rel = path.relative_to(ROOT)
        if "__pycache__" not in rel.parts:
            banned.append(str(rel))
    for path in ROOT.rglob("*.pyo"):
        banned.append(str(path.relative_to(ROOT)))
    assert banned == []


def test_no_absolute_build_paths_leak():
    offenders = []
    text_suffixes = {".py", ".md", ".txt", ".csv", ".yaml", ".yml", ".toml", ".cff", ".json"}
    markers = [
        "/" + "mnt" + "/",
        "/" + "home" + "/",
        "/" + "Users" + "/",
        "C:" + "\\" + "Users",
        "/usr/" + "bin/" + "python",
    ]
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in text_suffixes:
            content = path.read_text(errors="ignore")
            if any(m in content for m in markers):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], offenders


def test_requirements_are_pinned():
    lines = [x.strip() for x in (ROOT / "requirements.txt").read_text().splitlines()
             if x.strip() and not x.startswith("#")]
    assert lines
    assert all("==" in x for x in lines)


def test_output_dirs_are_v1_8_1_only():
    outputs = ROOT / "outputs"
    if outputs.exists():
        dirs = [p.name for p in outputs.iterdir() if p.is_dir()]
        assert dirs == ["v1_8_1"], dirs
