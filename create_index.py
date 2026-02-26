import os
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterTimeoutOptions
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

query = f"CREATE PRIMARY INDEX ON `{bucket_name}`"
print(f"Running query: {query}")
cluster.query(query).execute()
print("Primary index created successfully.")
