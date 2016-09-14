#!/bin/sh
export DISPATCH=$(grep -r DispatchAction --include=*.java | grep -v Lookup | grep -v import | wc -l)
export LOOKUP=$(grep -r LookupDispatchAction --include=*.java | grep -v import | wc -l)
echo $DISPATCH $LOOKUP
