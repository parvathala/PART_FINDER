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
timeout_options = ClusterTimeoutOptions(connect_timeout=timedelta(seconds=10))
options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

fields_to_index = [
    "product_id_pcs",
    "product_id_triad",
    "distributor_part_number",
    "alternate_part_number"
]

for field in fields_to_index:
    index_name = f"idx_search_{field}"
    query = f"CREATE INDEX {index_name} IF NOT EXISTS ON `{bucket_name}` (UPPER(TO_STRING({field})))"
    try:
        print(f"Executing: {query}")
        cluster.query(query).execute()
        print(f"Successfully created index {index_name}")
    except Exception as e:
        print(f"Error creating index {index_name}: {e}")

print("Index creation script finished.")
