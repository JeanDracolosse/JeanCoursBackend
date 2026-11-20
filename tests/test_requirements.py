import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def whenComparingDependencyFiles_thenPyprojectMatchesRequirements():
    # Given
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").split()

    # When
    deployed = pyproject["project"]["dependencies"]

    # Then
    assert sorted(deployed) == sorted(requirements)
