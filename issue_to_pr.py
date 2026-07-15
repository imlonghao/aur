#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ISSUE_TITLE_RE = re.compile(
    r"^(?P<package>[A-Za-z0-9@._+-]+): updated from "
    r"(?P<old>[A-Za-z0-9._+]+) to (?P<new>[A-Za-z0-9._+]+)$"
)
PKGVER_RE = re.compile(r"^pkgver=(?P<version>[^\s#]+)$", re.MULTILINE)
CHECKSUM_START_RE = re.compile(
    r"^(?P<name>(?:ck|md5|sha1|sha224|sha256|sha384|sha512|b2)sums"
    r"(?:_[A-Za-z0-9_]+)?)=\("
)


class UpdateError(RuntimeError):
    pass


class IgnoredIssue(UpdateError):
    pass


def parse_event(event: dict) -> dict[str, str]:
    if event.get("action") != "opened":
        raise UpdateError("only newly opened issues are supported")

    issue = event.get("issue") or {}
    labels = {
        label.get("name")
        for label in issue.get("labels", [])
        if isinstance(label, dict)
    }
    if "out-of-date" not in labels:
        raise IgnoredIssue("issue does not have the out-of-date label")

    match = ISSUE_TITLE_RE.fullmatch(issue.get("title", ""))
    if not match:
        raise UpdateError(
            "issue title must match '<package>: updated from <old> to <new>'"
        )

    number = event.get("number", issue.get("number"))
    if not isinstance(number, int) or number <= 0:
        raise UpdateError("issue number is missing or invalid")

    result = match.groupdict()
    result["issue_number"] = str(number)
    return result


def checksum_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines(keepends=True)
    blocks: dict[str, str] = {}
    index = 0
    while index < len(lines):
        match = CHECKSUM_START_RE.match(lines[index])
        if not match:
            index += 1
            continue

        start = index
        while index < len(lines) and not lines[index].rstrip().endswith(")"):
            index += 1
        if index == len(lines):
            raise UpdateError(f"unterminated checksum array: {match.group('name')}")
        index += 1
        blocks[match.group("name")] = "".join(lines[start:index])
    return blocks


def replace_checksum_blocks(pkgbuild: str, generated: str) -> str:
    replacements = checksum_blocks(generated)
    if not replacements:
        raise UpdateError("makepkg -g did not generate any checksum arrays")

    lines = pkgbuild.splitlines(keepends=True)
    output: list[str] = []
    replaced: set[str] = set()
    index = 0
    while index < len(lines):
        match = CHECKSUM_START_RE.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue

        name = match.group("name")
        start = index
        while index < len(lines) and not lines[index].rstrip().endswith(")"):
            index += 1
        if index == len(lines):
            raise UpdateError(f"unterminated checksum array: {name}")
        index += 1

        if name in replacements:
            output.append(replacements[name])
            replaced.add(name)
        else:
            output.extend(lines[start:index])

    missing = set(replacements) - replaced
    if missing:
        raise UpdateError(
            "makepkg -g generated checksum arrays not present in PKGBUILD: "
            + ", ".join(sorted(missing))
        )
    return "".join(output)


def replace_pkgver(pkgbuild: str, old_version: str, new_version: str) -> str:
    matches = list(PKGVER_RE.finditer(pkgbuild))
    if len(matches) != 1:
        raise UpdateError("PKGBUILD must contain exactly one simple pkgver assignment")
    current = matches[0].group("version")
    if current != old_version:
        raise UpdateError(
            f"issue expects pkgver {old_version}, but PKGBUILD contains {current}"
        )
    return PKGVER_RE.sub(f"pkgver={new_version}", pkgbuild, count=1)


def generate_checksums(package_dir: Path, makepkg_user: str | None) -> str:
    command = ["makepkg", "-g"]
    if makepkg_user:
        command = ["runuser", "-u", makepkg_user, "--", *command]
    process = subprocess.run(
        command,
        cwd=package_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if process.returncode != 0:
        raise UpdateError(f"makepkg -g failed:\n{process.stdout}")
    return process.stdout


def append_env(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as env_file:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise UpdateError(f"multiline value is not allowed for {key}")
            env_file.write(f"{key}={value}\n")


def update_from_event(
    event_path: Path, repo_root: Path, env_file: Path, makepkg_user: str | None
) -> dict[str, str]:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    details = parse_event(event)

    package_dir = (repo_root / details["package"]).resolve()
    if package_dir.parent != repo_root.resolve() or not package_dir.is_dir():
        raise UpdateError(f"package directory does not exist: {details['package']}")
    pkgbuild_path = package_dir / "PKGBUILD"
    if not pkgbuild_path.is_file():
        raise UpdateError(f"PKGBUILD does not exist for {details['package']}")

    original = pkgbuild_path.read_text(encoding="utf-8")
    updated = replace_pkgver(original, details["old"], details["new"])
    pkgbuild_path.write_text(updated, encoding="utf-8")

    try:
        generated = generate_checksums(package_dir, makepkg_user)
        updated = replace_checksum_blocks(updated, generated)
        pkgbuild_path.write_text(updated, encoding="utf-8")
    except Exception:
        pkgbuild_path.write_text(original, encoding="utf-8")
        raise

    values = {
        "PACKAGE": details["package"],
        "OLD_VERSION": details["old"],
        "NEW_VERSION": details["new"],
        "ISSUE_NUMBER": details["issue_number"],
        "BRANCH": f"automation/issue-{details['issue_number']}-{details['package']}",
        "COMMIT_MESSAGE": (
            f"{details['package']}: {details['old']} -> {details['new']}"
        ),
    }
    append_env(env_file, values)
    return values


def api_request(url: str, token: str, method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/json",
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        response_body = error.read().decode(errors="replace")
        raise UpdateError(
            f"Gitea API {method} {url} failed with {error.code}: {response_body}"
        ) from error


def create_pull_request(
    api_url: str,
    owner: str,
    repo: str,
    token: str,
    branch: str,
    base: str,
    title: str,
    issue_number: str,
) -> str:
    pulls_url = f"{api_url.rstrip('/')}/repos/{owner}/{repo}/pulls"
    query = urlencode({"state": "open", "page": 1, "limit": 50})
    for pull in api_request(f"{pulls_url}?{query}", token):
        if (
            pull.get("head", {}).get("ref") == branch
            and pull.get("base", {}).get("ref") == base
        ):
            return pull.get("html_url", "existing pull request")

    pull = api_request(
        pulls_url,
        token,
        method="POST",
        body={
            "base": base,
            "body": f"Closes #{issue_number}\n\nCreated automatically from the version update issue.",
            "head": branch,
            "title": title,
        },
    )
    return pull.get("html_url", "pull request created")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create package update PRs from issues")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update = subparsers.add_parser("update")
    update.add_argument("--event", type=Path, required=True)
    update.add_argument("--env-file", type=Path, required=True)
    update.add_argument("--makepkg-user")

    create_pr = subparsers.add_parser("create-pr")
    create_pr.add_argument("--api-url", default="https://git.esd.cc/api/v1")
    create_pr.add_argument("--owner", default="imlonghao")
    create_pr.add_argument("--repo", default="aur")
    create_pr.add_argument("--base", default="master")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "update":
            try:
                values = update_from_event(
                    args.event,
                    Path.cwd(),
                    args.env_file,
                    args.makepkg_user,
                )
            except IgnoredIssue as error:
                append_env(args.env_file, {"SKIP_UPDATE": "1"})
                print(f"Skipping: {error}")
                return 0
            print(values["COMMIT_MESSAGE"])
            return 0

        token = os.environ["GITEA_BOT_TOKEN"]
        url = create_pull_request(
            args.api_url,
            args.owner,
            args.repo,
            token,
            os.environ["BRANCH"],
            args.base,
            os.environ["COMMIT_MESSAGE"],
            os.environ["ISSUE_NUMBER"],
        )
        print(url)
        return 0
    except (UpdateError, KeyError, json.JSONDecodeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
