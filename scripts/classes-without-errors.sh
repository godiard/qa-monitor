#!/bin/sh
grep "<ClassStats" $1 |grep "bugs=\"0\"" |  wc -l
