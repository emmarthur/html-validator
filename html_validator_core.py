"""
HTML structure checker — Visitor + manifest rules (Greg Wilson, sdxpy Ch. 11).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from bs4 import BeautifulSoup, NavigableString, Tag


class Visitor:
    def visit(self, node: Any) -> None:
        if isinstance(node, NavigableString):
            self._text(node)
        elif isinstance(node, Tag):
            self._tag_enter(node)
            for child in node:
                self.visit(child)
            self._tag_exit(node)

    def _tag_enter(self, node: Tag) -> None:
        pass

    def _tag_exit(self, node: Tag) -> None:
        pass

    def _text(self, node: NavigableString) -> None:
        pass


class Catalog(Visitor):
    def __init__(self) -> None:
        super().__init__()
        self.catalog: dict[str, set[str]] = {}

    def _tag_enter(self, node: Tag) -> None:
        if node.name not in self.catalog:
            self.catalog[node.name] = set()
        for child in node:
            if isinstance(child, Tag):
                self.catalog[node.name].add(child.name)


class Check(Visitor):
    def __init__(self, manifest: dict[str, set[str]]) -> None:
        super().__init__()
        self.manifest = manifest
        self.problems: dict[str, set[str]] = {}

    def _tag_enter(self, node: Tag) -> None:
        allowed = self.manifest.get(node.name)
        if allowed is None:
            return
        actual = {child.name for child in node if isinstance(child, Tag)}
        errors = actual - allowed
        if errors:
            errors |= self.problems.get(node.name, set())
            self.problems[node.name] = errors


def default_manifests_dir() -> Path:
    return Path(__file__).resolve().parent / "data" / "manifests"


def load_manifest_yaml(text: str) -> dict[str, set[str]]:
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise ValueError("Manifest must be a YAML mapping of tag -> child tags")
    result: dict[str, set[str]] = {}
    for key, value in raw.items():
        if isinstance(value, list):
            result[str(key)] = {str(v) for v in value}
        else:
            raise ValueError(f"Manifest entry for {key} must be a list")
    return result


def load_manifest_file(path: Path) -> dict[str, set[str]]:
    return load_manifest_yaml(path.read_text(encoding="utf-8"))


def list_preset_manifests() -> list[dict[str, str]]:
    root = default_manifests_dir()
    if not root.is_dir():
        return []
    out: list[dict[str, str]] = []
    for path in sorted(root.glob("*.yml")):
        out.append({"id": path.stem, "name": path.stem.replace("-", " ").title()})
    return out


def get_preset_manifest(manifest_id: str) -> dict[str, set[str]]:
    path = default_manifests_dir() / f"{manifest_id}.yml"
    if not path.is_file():
        raise FileNotFoundError(f"Unknown manifest: {manifest_id}")
    return load_manifest_file(path)


@dataclass
class AnalysisResult:
    catalog: dict[str, list[str]]
    problems: dict[str, list[str]]
    ok: bool
    root_found: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "catalog": self.catalog,
            "problems": self.problems,
            "ok": self.ok,
            "root_found": self.root_found,
        }


def analyze_html(
    html: str,
    manifest: dict[str, set[str]],
) -> AnalysisResult:
    doc = BeautifulSoup(html, "html.parser")
    root = doc.html
    if root is None:
        return AnalysisResult(catalog={}, problems={}, ok=False, root_found=False)

    cataloger = Catalog()
    cataloger.visit(root)
    catalog = {k: sorted(v) for k, v in cataloger.catalog.items()}

    checker = Check(manifest)
    checker.visit(root)
    problems = {k: sorted(v) for k, v in checker.problems.items()}

    return AnalysisResult(
        catalog=catalog,
        problems=problems,
        ok=len(problems) == 0,
        root_found=True,
    )
