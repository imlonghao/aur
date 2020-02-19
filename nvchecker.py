#!/usr/bin/env python3

import os
import sys
import json
from github import Github

g = Github(os.getenv('GITHUB_TOKEN'))
repo = g.get_repo('imlonghao/aur')
open_issues = repo.get_issues(state='open', labels=['out-of-date'])

for line in sys.stdin:
    this = json.loads(line)
    print(this)
    if this['event'] != 'updated':
        continue
    title = '%s: updated from %s to %s' % (this['name'], this['old_version'], this['version'])
    opened = False
    for issue in open_issues:
        if issue.title.startswith(this['name'] + ': '):
            opened = True
            if issue.title != title:
                issue.edit(title=title)
            break
    if not opened:
        repo.create_issue(title=title, labels=['out-of-date'], assignee='imlonghao')
