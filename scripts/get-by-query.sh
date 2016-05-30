#!/bin/sh
export GET_BY_QUERY=$(grep -r getByQuery * --exclude=*.class | grep -v WithParams | wc -l)
export GET_UNIQUE_BY_QUERY=$(grep -r getUniqueByQuery * --exclude=*.class | grep -v WithParams | wc -l)
export EXECUTE_QUERY=$(grep -r Db.executeQuery * --exclude=*.class | grep -v WithParams | wc -l)
export GET_BY_QUERY_WITH_PARAMS=$(grep -r getByQueryWithParams * --exclude=*.class | wc -l)
export GET_UNIQUE_BY_QUERY_WITH_PARAMS=$(grep -r getUniqueByQueryWithParams * --exclude=*.class | wc -l)
export EXECUTE_QUERY_WITH_PARAMS=$(grep -r executeQueryWithParams * --exclude=*.class | wc -l)
echo $GET_BY_QUERY $GET_UNIQUE_BY_QUERY $EXECUTE_QUERY $GET_BY_QUERY_WITH_PARAMS $GET_UNIQUE_BY_QUERY_WITH_PARAMS $EXECUTE_QUERY_WITH_PARAMS
