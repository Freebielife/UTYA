import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("publication_bundle", Path(__file__).resolve().parents[1] / "scripts/publication_bundle.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicationBundleTest(unittest.TestCase):
    def fixture(self, parent):
        project = Path(parent) / "project"
        (project / "data").mkdir(parents=True)
        snapshot = {"token": "test", "schema": 1, "updated": 123}
        (project / "data/snapshot.json").write_text(json.dumps(snapshot))
        (project / "index.html").write_text('<script id="snapshot" type="application/json">' + json.dumps(snapshot) + '</script>')
        return project

    def test_exports_matching_bundle_to_public_loader_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            project = self.fixture(temp)
            module.export_bundle(project)
            for relative in ("index.html", "data/snapshot.json"):
                self.assertEqual((Path(temp) / relative).read_bytes(), (project / relative).read_bytes())

    def test_mismatch_preserves_previous_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            project = self.fixture(temp)
            module.export_bundle(project)
            old = (Path(temp) / "index.html").read_bytes()
            (project / "data/snapshot.json").write_text('{"updated":999}')
            with self.assertRaises(ValueError):
                module.export_bundle(project)
            self.assertEqual((Path(temp) / "index.html").read_bytes(), old)
            self.assertEqual(json.loads((Path(temp) / "data/snapshot.json").read_text())["updated"], 123)
