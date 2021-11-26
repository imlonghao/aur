#!/usr/bin/env python3

import os
import sys
import json
import giteapy
import subprocess

owner = "imlonghao"
repo = "aur"

configuration = giteapy.Configuration()
configuration.host = "https://git.esd.cc/api/v1"
configuration.api_key["token"] = os.environ["GITEA_BOT_TOKEN"]
api_instance = giteapy.IssueApi(giteapy.ApiClient(configuration))
open_issues = api_instance.issue_list_issues(
    owner, repo, state="open", labels="out-of-date", page=-1
)

for issue in open_issues:
    pkgname = issue.title.split(":")[0]
    issue_version = issue.title.split(" ")[-1]
    repo_version = subprocess.getoutput(
        f"bash -c 'source {pkgname}/PKGBUILD; echo $pkgver'"
    )
    print(f"{pkgname}: wants {issue_version}, now {repo_version}")
    if issue_version == repo_version:
        api_instance.issue_edit_issue(owner, repo, issue.id, body={"state": "closed"})
