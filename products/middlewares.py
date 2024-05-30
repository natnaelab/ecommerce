import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class QueryLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        for query in connection.queries:
            print(query)
            logger.debug(
                f"SQL Query: {query['sql']}\nStack Trace: {query['stacktrace']}"
            )
        return response
