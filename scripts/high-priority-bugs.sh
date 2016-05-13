#!/bin/sh
grep "priority=\"1\"" $1 | wc -l
