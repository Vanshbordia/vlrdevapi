"""Tests verifying that every namespace with @sanitize_and_validate has a .pyi type stub."""

import ast
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src" / "vlrdevapi"


def _find_namespace_files() -> list[Path]:
    """Return all namespace python files that use @sanitize_and_validate."""
    result = []
    for py_file in SRC_DIR.rglob("*namespace*.py"):
        content = py_file.read_text(encoding="utf-8")
        if "@sanitize_and_validate" in content:
            result.append(py_file)
    return sorted(result)


def _find_pyi_for(py_file: Path) -> Path:
    """Return the expected .pyi path for a given .py file."""
    return py_file.with_suffix(".pyi")


def _get_decorated_methods(py_file: Path) -> list[tuple[str, int]]:
    """Parse a .py file and return (name, num_params) for each @sanitize_and_validate method."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    decorated: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_decorator = any(
                isinstance(d, ast.Name) and d.id == "sanitize_and_validate"
                for d in node.decorator_list
            )
            if has_decorator:
                args = node.args
                # Count only non-self positional params
                base_count = len(args.args)
                if base_count > 0 and args.args[0].arg == "self":
                    base_count -= 1
                # Add keyword-only params (after *, or after *args)
                kwonly_count = len(args.kwonlyargs)
                param_count = base_count + kwonly_count
                decorated.append((node.name, param_count))
    return decorated


def _get_decorated_method_params(py_file: Path) -> dict[str, list[str]]:
    """Parse a .py file and return {name: [param_names]} for each @sanitize_and_validate method."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    decorated: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_decorator = any(
                isinstance(d, ast.Name) and d.id == "sanitize_and_validate"
                for d in node.decorator_list
            )
            if has_decorator:
                params = [a.arg for a in node.args.args if a.arg != "self"]
                params.extend(a.arg for a in node.args.kwonlyargs)
                decorated[node.name] = params
    return decorated


def _get_stub_methods(pyi_file: Path) -> list[tuple[str, int]]:
    """Parse a .pyi file and return (name, num_params) for each method definition."""
    tree = ast.parse(pyi_file.read_text(encoding="utf-8"))
    methods: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip @property declarations — they don't need @sanitize_and_validate
            is_property = any(
                isinstance(d, ast.Name) and d.id == "property"
                for d in node.decorator_list
            )
            if is_property:
                continue
            args = node.args
            base_count = len(args.args)
            if base_count > 0 and args.args[0].arg == "self":
                base_count -= 1
            kwonly_count = len(args.kwonlyargs)
            param_count = base_count + kwonly_count
            methods.append((node.name, param_count))
    return methods


def _get_stub_method_params(pyi_file: Path) -> dict[str, list[str]]:
    """Parse a .pyi file and return {name: [param_names]} for each method definition."""
    tree = ast.parse(pyi_file.read_text(encoding="utf-8"))
    methods: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_property = any(
                isinstance(d, ast.Name) and d.id == "property"
                for d in node.decorator_list
            )
            if is_property:
                continue
            params = [a.arg for a in node.args.args if a.arg != "self"]
            params.extend(a.arg for a in node.args.kwonlyargs)
            methods[node.name] = params
    return methods


def _get_class_init_params(file_path: Path) -> dict[str, list[str]]:
    """Extract __init__ parameter names for each class definition in file_path."""
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    inits: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                    params = [a.arg for a in item.args.args if a.arg != "self"]
                    params.extend(a.arg for a in item.args.kwonlyargs)
                    inits[node.name] = params
    return inits


class TestAllStubsSyntax:
    """Every .pyi file must be syntactically valid."""

    @pytest.mark.parametrize(
        "pyi_file",
        sorted(SRC_DIR.rglob("*.pyi")),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_stub_syntax_valid(self, pyi_file: Path):
        content = pyi_file.read_text(encoding="utf-8")
        ast.parse(content, filename=str(pyi_file))


class TestPyiExistence:
    """Every namespace python file with @sanitize_and_validate must have a .pyi stub."""

    @pytest.mark.parametrize(
        "py_file",
        _find_namespace_files(),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_pyi_exists(self, py_file: Path):
        pyi = _find_pyi_for(py_file)
        assert pyi.is_file(), f"Missing .pyi stub for {py_file}"


class TestPyiCompleteness:
    """Every @sanitize_and_validate method must have a matching stub declaration."""

    @pytest.mark.parametrize(
        "py_file",
        _find_namespace_files(),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_stub_has_all_methods(self, py_file: Path):
        pyi = _find_pyi_for(py_file)
        if not pyi.is_file():
            pytest.skip(f"No .pyi stub for {py_file}")

        py_methods = dict(_get_decorated_methods(py_file))
        stub_methods = dict(_get_stub_methods(pyi))

        for name in py_methods:
            assert name in stub_methods, (
                f"Method {name}() decorated with @sanitize_and_validate in "
                f"{py_file.relative_to(SRC_DIR)} is missing from the .pyi stub"
            )

    @pytest.mark.parametrize(
        "py_file",
        _find_namespace_files(),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_stub_param_counts_match(self, py_file: Path):
        pyi = _find_pyi_for(py_file)
        if not pyi.is_file():
            pytest.skip(f"No .pyi stub for {py_file}")

        py_methods = dict(_get_decorated_methods(py_file))
        stub_methods = dict(_get_stub_methods(pyi))

        for name, py_count in py_methods.items():
            if name not in stub_methods:
                continue
            stub_count = stub_methods[name]
            assert py_count == stub_count, (
                f"Parameter count mismatch for {name}() in "
                f"{py_file.relative_to(SRC_DIR)}: "
                f".py has {py_count} params, .pyi has {stub_count} params"
            )

    @pytest.mark.parametrize(
        "py_file",
        _find_namespace_files(),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_stub_param_names_match(self, py_file: Path):
        pyi = _find_pyi_for(py_file)
        if not pyi.is_file():
            pytest.skip(f"No .pyi stub for {py_file}")

        py_params = _get_decorated_method_params(py_file)
        stub_params = _get_stub_method_params(pyi)

        for name, py_p in py_params.items():
            if name not in stub_params:
                continue
            stub_p = stub_params[name]
            assert py_p == stub_p, (
                f"Parameter name mismatch for {name}() in "
                f"{py_file.relative_to(SRC_DIR)}: "
                f".py has {py_p}, .pyi has {stub_p}"
            )

    @pytest.mark.parametrize(
        "py_file",
        _find_namespace_files(),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_stub_init_params_match(self, py_file: Path):
        pyi = _find_pyi_for(py_file)
        if not pyi.is_file():
            pytest.skip(f"No .pyi stub for {py_file}")

        py_inits = _get_class_init_params(py_file)
        stub_inits = _get_class_init_params(pyi)

        for cls_name, py_params in py_inits.items():
            if cls_name in stub_inits:
                stub_params = stub_inits[cls_name]
                assert py_params == stub_params, (
                    f"__init__ parameter mismatch for class {cls_name} in "
                    f"{py_file.relative_to(SRC_DIR)}: "
                    f".py has {py_params}, .pyi has {stub_params}"
                )


class TestPyiNoExtraMethods:
    """Stubs should not declare methods that don't exist in the .py file."""

    @pytest.mark.parametrize(
        "py_file",
        _find_namespace_files(),
        ids=lambda p: str(p.relative_to(SRC_DIR)),
    )
    def test_stub_no_extra_methods(self, py_file: Path):
        pyi = _find_pyi_for(py_file)
        if not pyi.is_file():
            pytest.skip(f"No .pyi stub for {py_file}")

        py_methods = dict(_get_decorated_methods(py_file))
        stub_methods = dict(_get_stub_methods(pyi))
        exempt = {"__init__"}

        for name in stub_methods:
            if name in exempt:
                continue
            assert name in py_methods, (
                f"Method {name}() in .pyi stub at "
                f"{pyi.relative_to(SRC_DIR)} has no corresponding "
                f"@sanitize_and_validate method in the .py file. "
                f"If this is intentional, add a stub entry; "
                f"otherwise remove it."
            )
