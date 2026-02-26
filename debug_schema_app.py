import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
from datetime import timedelta
from dotenv import load_dotenv
import json

load_dotenv()
host = os.getenv("COUCHBASE_HOST", "couchbase://10.201.68.111")
username = os.getenv("COUCHBASE_USERNAME", "webdev")
password = os.getenv("COUCHBASE_PASSWORD", "webdev123")
auth = PasswordAuthenticator(username, password)
options = ClusterOptions(authenticator=auth)
cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

q = """
SELECT meta(d).id, d.* 
FROM `qgic-gg` AS d
WHERE d.class = 'com.pcs.api.productmaintenance.productcatalog.entity.Product' 
   OR d._class = 'com.pcs.api.productmaintenance.productcatalog.entity.Product'
LIMIT 1
"""
try:
    res = cluster.query(q)
    for row in res:
        print(json.dumps(row, indent=2))
except Exception as e:
    print('Error:', e)
