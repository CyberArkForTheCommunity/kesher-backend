from service.access_layer.get_connection import get_connection_to_rds


def execute_query(query: str):
    connection = get_connection_to_rds()
    cur = connection.cursor()
    cur.execute(query)
    query_results = cur.fetchall()
    return query_results
