#!/bin/sh
grep -ri "todo:" * --exclude=*.class --exclude-dir=docs --exclude=*jquery* --exclude=ui.*.js --exclude=tiny_mce*.js | wc -l
