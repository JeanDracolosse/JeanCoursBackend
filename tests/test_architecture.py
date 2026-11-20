import ast
from pathlib import Path

WEB_PACKAGE = Path(__file__).resolve().parents[1] / "jean_cours"
GARMIN_MODULES = ("garmin_sync", "garminconnect", "garth", "garmin_fit_sdk")


def _imported_modules(path: Path) -> set[str]:
    modules = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def whenScanningTheWebPackage_thenNoModuleImportsGarminCode():
    # Given
    modules_by_file = {path: _imported_modules(path) for path in WEB_PACKAGE.rglob("*.py")}

    # When
    offenders = {str(path.relative_to(WEB_PACKAGE)): sorted(module for module in modules if module.startswith(GARMIN_MODULES))
                 for path, modules in modules_by_file.items()}

    # Then
    assert {path: modules for path, modules in offenders.items() if modules} == {}
