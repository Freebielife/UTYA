"""Export the validated nested project to the repository publication paths."""
import json
import os
import re
from pathlib import Path


def export_bundle(project_root):
    project_root = Path(project_root).resolve()
    repository_root = project_root.parent
    page = (project_root / "index.html").read_bytes()
    snapshot = (project_root / "data/snapshot.json").read_bytes()
    embedded = re.search(rb'<script id="snapshot" type="application/json">(.*?)</script>', page, re.S)
    if not embedded or json.loads(embedded[1]) != json.loads(snapshot):
        raise ValueError("Publication page and snapshot differ; keep the previous bundle")
    for relative, content in (("data/snapshot.json", snapshot), ("index.html", page)):
        target = repository_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_bytes(content)
        os.replace(temporary, target)
