#!/bin/sh
../../ant.sh
../../tools/findbugs-3.0.1/bin/findbugs -project ../scripts/$2.fbp -textui -xml -low -output $1
