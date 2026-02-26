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

search_term = "TDI1000106"

q = """
SELECT product_id_pcs, product_id_triad, distributor_part_number, alternate_part_number
FROM `qgic-gg` AS d
WHERE SEARCH(d, $search_term, {"index": "qgic-gg._default.qafts"})
  AND d._class = 'com.pcs.api.productmaintenance.productcatalog.entity.Product'
LIMIT 20
"""
try:
    print(f"Executing FTS N1QL with query: {search_term}")
    res = cluster.query(q, QueryOptions(named_parameters={"search_term": search_term}))
    for row in res:
        print(row)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Error:', e)
