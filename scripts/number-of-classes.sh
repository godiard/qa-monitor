#!/bin/sh
export ALL_CLASSES=$(grep "<ClassStats" $1 | wc -l)
export WITHOUT_ERRORS=$(grep "<ClassStats" $1 |grep "bugs=\"0\"" |  wc -l)
echo $ALL_CLASSES $WITHOUT_ERRORS
