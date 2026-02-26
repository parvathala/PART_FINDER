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
bucket_name = os.getenv('COUCHBASE_BUCKET_NAME', 'qgic-gg')

auth = PasswordAuthenticator(username, password)
timeout_options = ClusterTimeoutOptions(connect_timeout=timedelta(seconds=10))
options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

query = "TDI1000106"
n1ql_query = f"""
    SELECT itemKey, legacyNumber, keyword, manufacturerPartNumber, distributorPartNumber
    FROM \{bucket_name}\
    WHERE UPPER(TO_STRING(itemKey)) = $search_term
       OR UPPER(TO_STRING(legacyNumber)) = $search_term
       OR UPPER(TO_STRING(keyword)) = $search_term
       OR UPPER(TO_STRING(manufacturerPartNumber)) = $search_term
       OR UPPER(TO_STRING(distributorPartNumber)) = $search_term
"""

try:
    print("Testing query directly like app.py...")
    query_result = cluster.query(
        n1ql_query,
        QueryOptions(named_parameters={'search_term': query})
    )
    results = [row for row in query_result.rows()]
    print(f"Results found: {len(results)}")
    for i, row in enumerate(results[:3]):
        print(f"Row {i}: {row}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
