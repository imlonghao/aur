#!/usr/bin/env python3

import os
import sys
import json
from gitlab import Gitlab

g = Gitlab('https://gitlab.com', job_token=os.environ['CI_JOB_TOKEN'])
repo = g.projects.get(19694297)
open_issues = repo.issues.list(state='opened', labels=['out-of-date'])

for line in sys.stdin:
    this = json.loads(line)
    print(this)
    if this['event'] != 'updated':
        continue
    title = '%s: updated from %s to %s' % (
        this['name'], this['old_version'], this['version'])
    opened = False
    for issue in open_issues:
        if issue.title.startswith(this['name'] + ': '):
            opened = True
            if issue.title != title:
                editable_issue = repo.issues.get(issue.iid, lazy=True)
                editable_issue.title = title
                editable_issue.save()
            break
    if not opened:
        repo.issues.create({
            'title': title,
            'labels': 'out-of-date',
            'assignee_ids': [535131]
        })
