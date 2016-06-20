#!/bin/sh
# Use bug-differences find-bugs-output1.xml find-bugs-output2.xml
# 
PATH_XML1=$1
PATH_XML2=$2
# create tmp txt files
../../tools/findbugs-3.0.1/bin/convertXmlToText $PATH_XML1 | awk -F " At " '{print $1}'| awk -F "[" '{print $1}' |  sort  > /tmp/$$-f1.txt
../../tools/findbugs-3.0.1/bin/convertXmlToText $PATH_XML2 | awk -F " At " '{print $1}'| awk -F "[" '{print $1}' |  sort  > /tmp/$$-f2.txt
diff -u /tmp/$$-f1.txt /tmp/$$-f2.txt | grep -v "^ " | grep -v "^@" | grep "^.H"
rm /tmp/$$-f1.txt
rm /tmp/$$-f2.txt
