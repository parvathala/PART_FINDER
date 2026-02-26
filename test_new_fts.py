import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions
from datetime import timedelta
import couchbase.search as search
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

search_term = "TDI1000106"
try:
    print(f"Executing SDK FTS search for: {search_term}")
    scope = cluster.bucket("qgic-gg").scope("_default")
    
    result = scope.search_query(
        "qafts",
        search.MatchQuery(search_term),
        limit=50
    )
    
    for row in result.rows():
        doc_id = row.id
        doc = cluster.bucket("qgic-gg").default_collection().get(doc_id).content_as[dict]
        # Filter by class
        if doc.get("_class") == "com.pcs.api.productmaintenance.productcatalog.entity.Product":
            print(f"Found Product ID: {doc_id}")
            print(f"  product_id_pcs: {doc.get('product_id_pcs')}")
            print(f"  product_id_triad: {doc.get('product_id_triad')}")

            
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Error:', e)
