import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, ClusterTimeoutOptions
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('COUCHBASE_HOST', 'couchbase://10.201.68.111')
username = os.getenv('COUCHBASE_USERNAME', 'webdev')
password = os.getenv('COUCHBASE_PASSWORD', 'webdev123')
bucket_name = os.getenv('COUCHBASE_BUCKET_NAME', 'qgic-gg')

auth = PasswordAuthenticator(username, password)
timeout_options = ClusterTimeoutOptions(connect_timeout=timedelta(seconds=10), query_timeout=timedelta(minutes=5))
options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

# Creating a highly optimized covering index specifically for the Product search
index_query = f"""
CREATE INDEX idx_product_search_opt IF NOT EXISTS ON `{bucket_name}`(
    class,
    content.legacyNumber,
    content.itemKey,
    content.manufacturerPartNumber,
    content.distributorPartNumber
) WHERE class = 'com.pcs.api.productmaintenance.productcatalog.entity.Product';
"""

try:
    print(f"Executing: {index_query}")
    cluster.query(index_query).execute()
    print(f"Successfully created index idx_product_search_opt")
except Exception as e:
    print(f"Error creating index: {e}")
