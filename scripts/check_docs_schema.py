"""Validate documentation TypeTable schemas against live Python library models.

Performs static and dynamic introspection of vlrdevapi against the official
documentation (English and all translations: es, pt-br, zh-cn).

Checks:
1. Python Signatures vs English Docs:
   - Ensures all function parameters in vlrdevapi match the '## Parameters' table.
2. Live Python Models vs English Docs:
   - Introspects Pydantic models and Enums from vlrdevapi.
   - Verifies that every documented field exists on the live Python model.
   - Catches phantom / outdated fields (e.g. 'dates', 'tag', 'score' on wrong models).
3. Cross-Language Parity (English vs es, pt-br, zh-cn):
   - Verifies that all translations have the exact same number of tables.
   - Verifies that tables appear in the exact same sequence.
   - Verifies that fields in every table match the exact same order and types.

CI/CD usage:
    uv run scripts/check_docs_schema.py
"""

from __future__ import annotations

import argparse
import inspect
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Any, NamedTuple

from pydantic import BaseModel

import vlrdevapi

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "official-docs" / "content" / "docs" / "reference"
LANGUAGES = ("es", "pt-br", "zh-cn")


class FieldDef(NamedTuple):
    name: str
    type_str: str
    default_str: str | None
    required: bool
    line: int


class TableDef(NamedTuple):
    heading: str
    model_name: str | None
    fields: dict[str, FieldDef]
    start_line: int


class DocDef(NamedTuple):
    path: Path
    sig: str | None
    ret_name: str | None
    tables: list[TableDef]


class Issue(NamedTuple):
    file_path: Path
    line: int
    category: str
    table_name: str
    message: str
    expected: str | None = None
    found: str | None = None


def get_all_subclasses(cls: type) -> set[type]:
    """Recursively collect all subclasses defined under vlrdevapi."""
    subclasses = set()
    for sub in cls.__subclasses__():
        if sub.__module__.startswith("vlrdevapi"):
            subclasses.add(sub)
        subclasses.update(get_all_subclasses(sub))
    return subclasses


def build_type_catalog() -> tuple[dict[str, type[BaseModel]], dict[str, type[Enum]]]:
    """Dynamically discover all Pydantic models and Enums from vlrdevapi."""
    models: dict[str, type[BaseModel]] = {
        cls.__name__: cls for cls in get_all_subclasses(BaseModel)
    }
    enums: dict[str, type[Enum]] = {
        cls.__name__: cls for cls in get_all_subclasses(Enum)
    }
    return models, enums


def parse_mdx(file_path: Path) -> DocDef:
    """Parse an MDX file into structured table definitions with line numbers."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Extract signature e.g. matches.completed(
    sig_m = re.search(r"##\s+Signature\s+```python\s*([a-zA-Z0-9_\.]+)\(", content)
    sig = sig_m.group(1) if sig_m else None

    # Extract return type name if present in ## Returns - Model
    ret_m = re.search(r"##\s+(?:Returns|Retorno|Retorno -|返回类型)\s+-\s+`?([a-zA-Z0-9_]+)`?", content)
    ret_name = ret_m.group(1) if ret_m else None

    # Locate each <TypeTable ... />
    table_matches = list(re.finditer(r"<TypeTable\s+type=\{\{(.*?)\}\}\s*/>", content, re.DOTALL))
    tables: list[TableDef] = []

    for m in table_matches:
        start_char = m.start()
        start_line = content[:start_char].count("\n") + 1

        # Look backward for closest markdown heading
        pre_text = content[:start_char]
        headings = list(re.finditer(r"(#{2,3}\s+[^\n]+)", pre_text))
        last_heading = headings[-1].group(1).strip() if headings else "Unknown Section"

        # Check for model name in heading: e.g. `CompletedMatchEntry` Fields
        name_matches = re.findall(r"`([a-zA-Z0-9_]+)`", last_heading)
        inferred_model = name_matches[0] if name_matches else None

        # Parse fields
        body = m.group(1)
        body_start_line = start_line
        field_matches = re.finditer(r"[\"']?([a-zA-Z0-9_]+)[\"']?\s*:\s*\{([^}]+)\}", body)
        fields: dict[str, FieldDef] = {}

        for fm in field_matches:
            fname = fm.group(1)
            fbody = fm.group(2)
            fline = body_start_line + body[:fm.start()].count("\n")

            tm = re.search(r"type\s*:\s*[\"']([^\"']+)[\"']", fbody)
            type_str = tm.group(1) if tm else ""

            dm = re.search(r"default\s*:\s*([^\n,]+)", fbody)
            default_str = dm.group(1).strip() if dm else None

            req_m = re.search(r"required\s*:\s*(true|false)", fbody, re.IGNORECASE)
            required = req_m.group(1).lower() == "true" if req_m else False

            fields[fname] = FieldDef(
                name=fname,
                type_str=type_str,
                default_str=default_str,
                required=required,
                line=fline,
            )

        tables.append(TableDef(
            heading=last_heading,
            model_name=inferred_model,
            fields=fields,
            start_line=start_line,
        ))

    return DocDef(
        path=file_path,
        sig=sig,
        ret_name=ret_name,
        tables=tables,
    )


def resolve_callable(sig: str) -> Any:
    """Dynamically resolve a Python callable from vlrdevapi using dot path."""
    obj: Any = vlrdevapi
    for part in sig.split("."):
        if not hasattr(obj, part):
            return None
        obj = getattr(obj, part)

    # If it is a namespace class with __call__, get __call__
    if hasattr(obj, "__call__") and not inspect.isfunction(obj) and not inspect.ismethod(obj):
        return obj.__call__
    return obj


def validate_doc_against_python(
    doc: DocDef,
    model_catalog: dict[str, type[BaseModel]],
    enum_catalog: dict[str, type[Enum]],
) -> list[Issue]:
    """Validate canonical English MDX against live Python signatures and models."""
    issues: list[Issue] = []
    if not doc.sig:
        return issues

    fn = resolve_callable(doc.sig)
    if fn is None:
        issues.append(Issue(
            file_path=doc.path,
            line=1,
            category="UNRESOLVED_CALLABLE",
            table_name="Signature",
            message=f"Callable '{doc.sig}' could not be resolved from vlrdevapi",
        ))
        return issues

    # 1. Parameter Table vs Signature
    try:
        sig_obj = inspect.signature(fn)
        py_params = [p for p in sig_obj.parameters if p != "self"]
    except (ValueError, TypeError):
        py_params = []

    param_tables = [t for t in doc.tables if "Parameters" in t.heading]
    if param_tables:
        ptable = param_tables[0]
        doc_params = list(ptable.fields.keys())
        missing_params = set(py_params) - set(doc_params)
        extra_params = set(doc_params) - set(py_params)

        for mp in sorted(missing_params):
            param_obj = sig_obj.parameters.get(mp)
            default_val = param_obj.default if param_obj else None
            issues.append(Issue(
                file_path=doc.path,
                line=ptable.start_line,
                category="MISSING_PARAMETER",
                table_name=ptable.heading,
                message=f"Parameter '{mp}' exists in Python signature {doc.sig}() but is missing from Parameters table",
                expected=f"{mp} (default: {default_val})",
            ))

        for ep in sorted(extra_params):
            fdef = ptable.fields[ep]
            issues.append(Issue(
                file_path=doc.path,
                line=fdef.line,
                category="EXTRA_PARAMETER",
                table_name=ptable.heading,
                message=f"Parameter '{ep}' documented in Parameters table does not exist in Python signature {doc.sig}()",
                found=ep,
            ))

        if not missing_params and not extra_params and py_params != doc_params:
            issues.append(Issue(
                file_path=doc.path,
                line=ptable.start_line,
                category="PARAMETER_ORDER_MISMATCH",
                table_name=ptable.heading,
                message="Parameter order mismatch between Python signature and documentation",
                expected=str(py_params),
                found=str(doc_params),
            ))

    # 2. Documented Models vs Live Python Models / Enums
    for table in doc.tables:
        if "Parameters" in table.heading:
            continue

        # Extract all candidate names from heading
        names = re.findall(r"`([a-zA-Z0-9_]+)`", table.heading)
        if not names and doc.ret_name and "Returns" in table.heading:
            names = [doc.ret_name]

        matched_model: type[BaseModel] | None = None
        matched_enum: type[Enum] | None = None

        # Check candidate names (try in order, preferring more specific e.g. SideStats over PlayerStats)
        for n in reversed(names):
            if n in model_catalog:
                matched_model = model_catalog[n]
                break
            if n in enum_catalog:
                matched_enum = enum_catalog[n]
                break

        if matched_model is not None:
            py_fields = matched_model.model_fields
            doc_fields = table.fields

            # Check for extra fields documented that do NOT exist in the Python model
            for doc_fname, fdef in doc_fields.items():
                if doc_fname not in py_fields:
                    issues.append(Issue(
                        file_path=doc.path,
                        line=fdef.line,
                        category="PHANTOM_FIELD",
                        table_name=matched_model.__name__,
                        message=f"Field '{doc_fname}' is documented in table '{matched_model.__name__}', but does NOT exist on the Python model '{matched_model.__module__}.{matched_model.__name__}'",
                        found=doc_fname,
                        expected=f"One of: {sorted(py_fields.keys())}",
                    ))

        elif matched_enum is not None:
            enum_members = set(matched_enum.__members__.keys())
            doc_fields = table.fields

            for doc_mname, fdef in doc_fields.items():
                if doc_mname not in enum_members:
                    issues.append(Issue(
                        file_path=doc.path,
                        line=fdef.line,
                        category="PHANTOM_ENUM_MEMBER",
                        table_name=matched_enum.__name__,
                        message=f"Enum member '{doc_mname}' is documented in '{matched_enum.__name__}', but does not exist in Python enum '{matched_enum.__module__}.{matched_enum.__name__}'",
                        found=doc_mname,
                        expected=f"One of: {sorted(enum_members)}",
                    ))

    return issues


def validate_translations_against_en(en_doc: DocDef, tr_doc: DocDef, lang: str) -> list[Issue]:
    """Validate a translation MDX against the canonical English MDX."""
    issues: list[Issue] = []

    # 1. Table count parity
    if len(en_doc.tables) != len(tr_doc.tables):
        issues.append(Issue(
            file_path=tr_doc.path,
            line=1,
            category="TABLE_COUNT_MISMATCH",
            table_name="Document",
            message=f"Table count mismatch: English document has {len(en_doc.tables)} tables, but {lang} translation has {len(tr_doc.tables)} tables",
            expected=f"{len(en_doc.tables)} tables",
            found=f"{len(tr_doc.tables)} tables",
        ))
        return issues

    # 2. Table-by-table structure, keys, order, and types
    for idx, (en_table, tr_table) in enumerate(zip(en_doc.tables, tr_doc.tables)):
        t_name = en_table.model_name or en_table.heading
        en_keys = list(en_table.fields.keys())
        tr_keys = list(tr_table.fields.keys())

        missing_in_tr = set(en_keys) - set(tr_keys)
        extra_in_tr = set(tr_keys) - set(en_keys)

        for m_key in sorted(missing_in_tr):
            en_fdef = en_table.fields[m_key]
            issues.append(Issue(
                file_path=tr_doc.path,
                line=tr_table.start_line,
                category="MISSING_TRANSLATION_FIELD",
                table_name=t_name,
                message=f"Table {idx} ({t_name}): Missing field '{m_key}' in {lang} translation",
                expected=f"Field '{m_key}' with type '{en_fdef.type_str}'",
            ))

        for e_key in sorted(extra_in_tr):
            tr_fdef = tr_table.fields[e_key]
            issues.append(Issue(
                file_path=tr_doc.path,
                line=tr_fdef.line,
                category="EXTRA_TRANSLATION_FIELD",
                table_name=t_name,
                message=f"Table {idx} ({t_name}): Extra field '{e_key}' found in {lang} translation that does not exist in English document",
                found=e_key,
            ))

        # Check exact field ordering
        if not missing_in_tr and not extra_in_tr and en_keys != tr_keys:
            # Pinpoint the first index where order diverges
            mismatch_idx = next(i for i, (ek, tk) in enumerate(zip(en_keys, tr_keys)) if ek != tk)
            issues.append(Issue(
                file_path=tr_doc.path,
                line=tr_table.fields[tr_keys[mismatch_idx]].line,
                category="FIELD_ORDER_MISMATCH",
                table_name=t_name,
                message=f"Table {idx} ({t_name}): Field ordering differs from English at position {mismatch_idx}",
                expected=f"Field '{en_keys[mismatch_idx]}'",
                found=f"Field '{tr_keys[mismatch_idx]}'",
            ))

        # Check field types
        for k in en_keys:
            if k in tr_table.fields:
                en_f = en_table.fields[k]
                tr_f = tr_table.fields[k]
                if en_f.type_str != tr_f.type_str:
                    issues.append(Issue(
                        file_path=tr_doc.path,
                        line=tr_f.line,
                        category="TYPE_MISMATCH",
                        table_name=t_name,
                        message=f"Table {idx} ({t_name}): Field '{k}' type mismatch",
                        expected=en_f.type_str,
                        found=tr_f.type_str,
                    ))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate documentation schemas against live Python library.")
    parser.add_argument("--strict", action="store_true", default=True, help="Exit with code 1 if any issues are found.")
    args = parser.parse_args()

    model_catalog, enum_catalog = build_type_catalog()

    en_files = sorted(
        p for p in DOCS_DIR.rglob("*.mdx")
        if not any(p.name.endswith(f".{lang}.mdx") for lang in LANGUAGES)
        and p.name != "index.mdx"
        and p.parent.name != "mcp"
    )

    all_issues: list[Issue] = []
    total_tables = 0
    total_translations = 0

    print("============================================================")
    print("VLRDEVAPI DOCUMENTATION SCHEMA VALIDATOR")
    print(f"Loaded {len(model_catalog)} Pydantic models & {len(enum_catalog)} Enums from live library")
    print(f"Auditing {len(en_files)} canonical reference docs across {len(LANGUAGES)} languages...")
    print("============================================================\n")

    for en_path in en_files:
        en_doc = parse_mdx(en_path)
        total_tables += len(en_doc.tables)

        # 1. Validate English against live Python library
        py_issues = validate_doc_against_python(en_doc, model_catalog, enum_catalog)
        all_issues.extend(py_issues)

        # 2. Validate each language translation against English
        for lang in LANGUAGES:
            tr_path = en_path.parent / f"{en_path.stem}.{lang}.mdx"
            if not tr_path.exists():
                all_issues.append(Issue(
                    file_path=en_path.parent / f"{en_path.stem}.{lang}.mdx",
                    line=1,
                    category="MISSING_FILE",
                    table_name="File",
                    message=f"Missing translation file: {tr_path.name}",
                ))
                continue

            total_translations += 1
            tr_doc = parse_mdx(tr_path)
            total_tables += len(tr_doc.tables)
            tr_issues = validate_translations_against_en(en_doc, tr_doc, lang)
            all_issues.extend(tr_issues)

    # Report results
    if all_issues:
        print(f"FAIL: Found {len(all_issues)} schema issue(s) across documentation:\n")
        # Group issues by file
        by_file: dict[Path, list[Issue]] = {}
        for iss in all_issues:
            by_file.setdefault(iss.file_path, []).append(iss)

        for fpath, issues_list in sorted(by_file.items(), key=lambda x: str(x[0])):
            rel_path = fpath.relative_to(REPO_ROOT) if fpath.is_relative_to(REPO_ROOT) else fpath
            print(f"--- {rel_path} ({len(issues_list)} issue{'s' if len(issues_list) > 1 else ''}) ---")
            for iss in issues_list:
                print(f"  Line {iss.line} [{iss.category}] in {iss.table_name}:")
                print(f"    Issue:    {iss.message}")
                if iss.expected is not None:
                    print(f"    Expected: {iss.expected}")
                if iss.found is not None:
                    print(f"    Found:    {iss.found}")
                print()

        print("============================================================")
        print("VALIDATION FAILED")
        print(f"  Total issues: {len(all_issues)} in {len(by_file)} files")
        print("============================================================")
        return 1

    print("SUCCESS: All documentation tables and translation schemas are 100% in sync with the live library!")
    print("============================================================")
    print("VALIDATION SUMMARY")
    print(f"  Canonical English docs checked: {len(en_files)}")
    print(f"  Translation files verified:     {total_translations}")
    print(f"  Total tables validated:         {total_tables}")
    print("  Schema mismatches:              0")
    print("============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
