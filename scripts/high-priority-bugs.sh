#!/bin/sh
grep "<FindBugsSummary" $1 | awk -F "priority_1=" '{print $2}'| awk -F '"' '{print $2}'
