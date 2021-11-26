#!/usr/bin/env python3

import os
import sys
import json
import giteapy

owner = "imlonghao"
repo = "aur"

configuration = giteapy.Configuration()
configuration.host = "https://git.esd.cc/api/v1"
configuration.api_key["token"] = os.environ["GITEA_BOT_TOKEN"]
api_instance = giteapy.IssueApi(giteapy.ApiClient(configuration))
open_issues = api_instance.issue_list_issues(
    owner, repo, state="open", labels="out-of-date", page=-1
)

for line in sys.stdin:
    this = json.loads(line)
    print(this)
    if this["event"] != "updated":
        continue
    title = "%s: updated from %s to %s" % (
        this["name"],
        this["old_version"],
        this["version"],
    )
    opened = False
    for issue in open_issues:
        if issue.title.startswith(this["name"] + ": "):
            opened = True
            if issue.title != title:
                api_instance.issue_edit_issue(
                    owner, repo, issue.id, body={"title": title}
                )
            break
    if not opened:
        api_instance.api_instance(
            owner,
            repo,
            body={
                "title": title,
                "assignee": "imlonghao",
                "labels": [1],
            },
        )
