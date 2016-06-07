#!/bin/sh
grep "<FindBugsSummary" $1 | awk -F "total_bugs=" '{print $2}'| awk -F '"' '{print $2}'
