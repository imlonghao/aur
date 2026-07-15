import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from issue_to_pr import (
    UpdateError,
    main,
    parse_event,
    replace_checksum_blocks,
    replace_pkgver,
    update_from_event,
)


class ParseEventTests(unittest.TestCase):
    def test_parses_nvchecker_issue(self):
        event = {
            "action": "opened",
            "number": 42,
            "issue": {
                "title": "chisel-tunnel: updated from 1.11.7 to 1.11.8",
                "labels": [{"name": "out-of-date"}],
            },
        }

        self.assertEqual(
            parse_event(event),
            {
                "package": "chisel-tunnel",
                "old": "1.11.7",
                "new": "1.11.8",
                "issue_number": "42",
            },
        )

    def test_rejects_issue_without_label(self):
        event = {
            "action": "opened",
            "number": 42,
            "issue": {
                "title": "chisel-tunnel: updated from 1.11.7 to 1.11.8",
                "labels": [],
            },
        }

        with self.assertRaisesRegex(UpdateError, "out-of-date"):
            parse_event(event)

    def test_workflow_skips_issue_without_label(self):
        event = {
            "action": "opened",
            "number": 42,
            "issue": {"title": "A regular issue", "labels": []},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_path = root / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            env_path = root / "env"
            argv = [
                "issue_to_pr.py",
                "update",
                "--event",
                str(event_path),
                "--env-file",
                str(env_path),
            ]

            with patch("sys.argv", argv):
                self.assertEqual(main(), 0)
            self.assertEqual(env_path.read_text(), "SKIP_UPDATE=1\n")

    def test_rejects_shell_metacharacters(self):
        event = {
            "action": "opened",
            "number": 42,
            "issue": {
                "title": "pkg: updated from 1.0 to 2.0; touch /tmp/pwned",
                "labels": [{"name": "out-of-date"}],
            },
        }

        with self.assertRaisesRegex(UpdateError, "title must match"):
            parse_event(event)


class PkgbuildUpdateTests(unittest.TestCase):
    def test_replaces_pkgver(self):
        self.assertEqual(
            replace_pkgver("pkgname=demo\npkgver=1.0\npkgrel=1\n", "1.0", "2.0"),
            "pkgname=demo\npkgver=2.0\npkgrel=1\n",
        )

    def test_rejects_stale_issue(self):
        with self.assertRaisesRegex(UpdateError, "expects pkgver 1.0"):
            replace_pkgver("pkgver=1.1\n", "1.0", "2.0")

    def test_replaces_multiline_and_arch_checksums(self):
        pkgbuild = (
            "source=('one' 'two')\n"
            "b2sums=('old-one'\n"
            "        'old-two')\n"
            "b2sums_x86_64=('old-arch')\n"
            "\npackage() {\n  true\n}\n"
        )
        generated = (
            "b2sums=('new-one'\n"
            "        'new-two')\n"
            "b2sums_x86_64=('new-arch')\n"
        )

        self.assertEqual(
            replace_checksum_blocks(pkgbuild, generated),
            (
                "source=('one' 'two')\n"
                "b2sums=('new-one'\n"
                "        'new-two')\n"
                "b2sums_x86_64=('new-arch')\n"
                "\npackage() {\n  true\n}\n"
            ),
        )

    def test_rejects_unexpected_checksum_type(self):
        with self.assertRaisesRegex(UpdateError, "not present"):
            replace_checksum_blocks(
                "source=('one')\nb2sums=('old')\n",
                "sha256sums=('new')\n",
            )

    def test_updates_pkgbuild_and_exports_workflow_values(self):
        event = {
            "action": "opened",
            "number": 42,
            "issue": {
                "title": "demo: updated from 1.0 to 2.0",
                "labels": [{"name": "out-of-date"}],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package_dir = root / "demo"
            package_dir.mkdir()
            pkgbuild = package_dir / "PKGBUILD"
            pkgbuild.write_text(
                "pkgname=demo\npkgver=1.0\nsource=('demo')\nb2sums=('old')\n",
                encoding="utf-8",
            )
            event_path = root / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            env_path = root / "env"

            with patch(
                "issue_to_pr.generate_checksums", return_value="b2sums=('new')\n"
            ):
                values = update_from_event(event_path, root, env_path, None)

            self.assertIn("pkgver=2.0", pkgbuild.read_text(encoding="utf-8"))
            self.assertIn("b2sums=('new')", pkgbuild.read_text(encoding="utf-8"))
            self.assertEqual(values["BRANCH"], "automation/issue-42-demo")
            self.assertIn("COMMIT_MESSAGE=demo: 1.0 -> 2.0", env_path.read_text())


if __name__ == "__main__":
    unittest.main()
