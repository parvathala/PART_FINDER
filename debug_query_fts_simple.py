import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("COUCHBASE_HOST", "couchbase://10.201.68.111")
username = os.getenv("COUCHBASE_USERNAME", "webdev")
password = os.getenv("COUCHBASE_PASSWORD", "webdev123")
auth = PasswordAuthenticator(username, password)
options = ClusterOptions(authenticator=auth)
cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

search_term = "68811030"

q = """
SELECT meta(d).id, product_id_pcs, product_id_triad 
FROM `qgic-gg` AS d
WHERE SEARCH(d, $search_term)
LIMIT 5
"""
try:
    res = cluster.query(q, QueryOptions(named_parameters={"search_term": search_term}))
    for row in res:
        print(row)
except Exception as e:
    print('Error:', e)
