#!/bin/bash
set -e
set -x

REPOS=$(git diff --dirstat=files,0 HEAD~1 | sed 's/^[ 0-9.]\+% //g' | grep -v '^\.' | grep '/' | sed 's/\/$//g')
DIRECTORY=$(pwd)

git config --global user.email "aur@esd.cc"
git config --global user.name "imlonghao"

git log -1 --pretty=%B >/tmp/commit

for REPO in $REPOS; do
    cd /tmp
    git clone ssh://aur@aur.archlinux.org/$REPO.git
    chmod 777 $REPO
    cd $REPO
    cp -r $DIRECTORY/$REPO/. .
    git add .
    git commit -m "$(fgrep "$REPO: " /tmp/commit | awk -F "$REPO: " '{print $2}')"
    git push
done
