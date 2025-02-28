import re
from pathlib import Path
from typing import List

import tomlkit
from polylith import repo


def transform_to_package(namespace: str, include: str) -> dict:
    path, _separator, brick = str.partition(include, f"/{namespace}/")

    return {"include": f"{namespace}/{brick}", "from": path}


def get_project_packages_from_polylith_section(data) -> dict:
    bricks = data["tool"].get("polylith", {}).get("bricks")

    return bricks if isinstance(bricks, dict) else {}


def get_hatch_project_packages(data) -> dict:
    hatch_data = data["tool"]["hatch"]
    build_data = hatch_data.get("build", {}) if isinstance(hatch_data, dict) else {}

    force_included = build_data.get("force-include")

    if force_included:
        return force_included

    return get_project_packages_from_polylith_section(data)


def get_project_package_includes(namespace: str, data) -> List[dict]:
    if repo.is_poetry(data):
        return data["tool"]["poetry"].get("packages", [])

    if repo.is_hatch(data):
        includes = get_hatch_project_packages(data)

        return [transform_to_package(namespace, key) for key in includes.keys()]

    return []


def get_project_name(data) -> str:
    if repo.is_pep_621_ready(data):
        return data["project"]["name"]

    return data["tool"]["poetry"]["name"]


def get_project_dependencies(data) -> dict:
    if repo.is_poetry(data):
        deps = data["tool"]["poetry"].get("dependencies", [])

        items = set(deps.keys())
    else:
        deps = data["project"].get("dependencies", [])

        items = {re.split(r"[\^~=!<>]", dep)[0] for dep in deps}

    return {"items": items, "source": repo.default_toml}


def read_toml_document(path: Path) -> tomlkit.TOMLDocument:
    with path.open(encoding="utf-8", errors="ignore") as f:
        return tomlkit.loads(f.read())
