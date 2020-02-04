#!/bin/bash
set -e

REPOS=$(git diff --dirstat=files,0 HEAD~1 | sed 's/^[ 0-9.]\+% //g' | sed 's/\/$//g' | fgrep -v .github/workflows)
COMMIT=$(git log -1 --pretty=%B)
DIRECTORY=$(pwd)

for REPO in $REPOS
do
    cd /tmp
    git clone ssh://aur@aur.archlinux.org/$REPO.git
    cd $REPO
    cp -r $DIRECTORY/$REPO/* .
    git add .
    git commit -m $(echo $COMMIT | grep $REPO | awk -F "$REPO: " '{print $2}')
    git push
done
