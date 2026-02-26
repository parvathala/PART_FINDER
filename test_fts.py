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

auth = PasswordAuthenticator(username, password)
options = ClusterOptions(authenticator=auth)

cluster = Cluster(host, options)
cluster.wait_until_ready(timedelta(seconds=10))

try:
    index_mgr = cluster.search_indexes()
    indexes = index_mgr.get_all_indexes()
    print("Existing FTS Indexes:")
    for idx in indexes:
        print(f" - {idx.name} (source: {idx.source_name})")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error checking indexes: {e}")
