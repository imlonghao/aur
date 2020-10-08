#!/bin/bash

rm -f /tmp/oldver /tmp/newver

for package in */
do
    source $package/PKGBUILD
    echo "$pkgname $pkgver" >> /tmp/oldver
done

nvchecker --logger=json -c nvchecker.ini | python nvchecker.py
