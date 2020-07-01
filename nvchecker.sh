#!/bin/ash

rm -f /tmp/oldver /tmp/newver

for package in */
do
    source $package/PKGBUILD
    echo "$pkgname $pkgver" >> /tmp/oldver
done

nvchecker --logger=json nvchecker.ini | python nvchecker.py
