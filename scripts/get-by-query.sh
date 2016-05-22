#!/bin/sh
export GET_BY_QUERY=$(grep -r getByQuery * --exclude=*.class | wc -l)
export GET_UNIQUE_BY_QUERY=$(grep -r getUniqueByQuery * --exclude=*.class | wc -l)
export GET_BY_QUERY_WITH_PARAMS=$(grep -r getByQueryWithParams * --exclude=*.class | wc -l)
export GET_UNIQUE_BY_QUERY_WITH_PARAMS=$(grep -r getUniqueByQueryWithParams * --exclude=*.class | wc -l)
echo $GET_BY_QUERY $GET_UNIQUE_BY_QUERY $GET_BY_QUERY_WITH_PARAMS $GET_UNIQUE_BY_QUERY_WITH_PARAMS
