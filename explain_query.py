import os
import json
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

query = "1000"
n1ql_query = f"""
EXPLAIN SELECT content.itemKey as product_id_pcs, content.legacyNumber as product_id_triad, content.distributorPartNumber as distributor_part_number, content.manufacturerPartNumber as alternate_part_number
FROM `qgic-gg` 
WHERE class = "com.pcs.api.productmaintenance.productcatalog.entity.Product"
  AND (
    content.legacyNumber LIKE '%1000%'
    OR content.itemKey = '1000'
    OR content.distributorPartNumber = '1000'
    OR content.manufacturerPartNumber = '1000'
  )
LIMIT 50
"""
try:
    print(f"Executing EXPLAIN:")
    res = cluster.query(n1ql_query)
    for row in res:
        print(json.dumps(row, indent=2))
except Exception as e:
    print('Error:', e)
