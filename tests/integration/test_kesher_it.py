from service.access_layer.get_connection import get_connection_to_rds

def test_connection_to_rds_and_run_simple_query():
    connection = get_connection_to_rds()
    cur = connection.cursor()
    cur.execute("""SELECT now()""")
    query_results = cur.fetchall()
