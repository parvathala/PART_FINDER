import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, ClusterTimeoutOptions, QueryOptions
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('COUCHBASE_HOST', 'couchbase://10.201.68.111')
username = os.getenv('COUCHBASE_USERNAME', 'webdev')
password = os.getenv('COUCHBASE_PASSWORD', 'webdev123')
bucket_name = 'qgic-gg'

auth = PasswordAuthenticator(username, password)
timeout_options = ClusterTimeoutOptions(connect_timeout=timedelta(seconds=10))
options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

query = "TDI1000106"
n1ql_query = f"""
    SELECT PRODUCT_ID_PCS, PRODUCT_ID_TRIAD, DISTRIBUTOR_PART_NUMBER, ALTERNATE_PART_NUMBER
    FROM `{bucket_name}`
    WHERE UPPER(TO_STRING(PRODUCT_ID_PCS)) = $search_term
       OR UPPER(TO_STRING(PRODUCT_ID_TRIAD)) = $search_term
       OR UPPER(TO_STRING(DISTRIBUTOR_PART_NUMBER)) = $search_term
       OR UPPER(TO_STRING(ALTERNATE_PART_NUMBER)) = $search_term
"""

try:
    print(f"Executing exact query from app.py: {query}")
    query_result = cluster.query(
        n1ql_query,
        QueryOptions(named_parameters={'search_term': query})
    )
    results_dict = [row for row in query_result.rows()]
    print(f"Raw N1QL Rows retrieved: {len(results_dict)}")
    
    unique_results = []
    seen = set()
    for row in results_dict:
        t = tuple(sorted(row.items()))
        if t not in seen:
            seen.add(t)
            unique_results.append(row)
            
    print(f"Unique results deduplicated: {len(unique_results)}")
    if unique_results:
        print(f"Sample row: {unique_results[0]}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
