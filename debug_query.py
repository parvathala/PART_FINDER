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
timeout_options = ClusterTimeoutOptions(
    connect_timeout=timedelta(seconds=10),
    query_timeout=timedelta(minutes=5)
)
options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

query = "68811030"
n1ql_query = f"""
    SELECT meta().id, `distributorpartnumber`, `distributorPartNumber`, `DISTRIBUTOR_PART_NUMBER`
    FROM `{bucket_name}`
    WHERE distributorpartnumber = $search_term
       OR distributorPartNumber = $search_term
       OR DISTRIBUTOR_PART_NUMBER = $search_term
       OR TO_STRING(distributorpartnumber) LIKE '%68811030%'
       OR TO_STRING(distributorPartNumber) LIKE '%68811030%'
    LIMIT 5
"""

try:
    print(f"Executing long-running full bucket scan for {query}...")
    query_result = cluster.query(
        n1ql_query,
        QueryOptions(
            named_parameters={'search_term': query},
            timeout=timedelta(minutes=5)
        )
    )
    results = [row for row in query_result.rows()]
    print(f"Results found: {len(results)}")
    for row in results:
        print(row)
        
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
