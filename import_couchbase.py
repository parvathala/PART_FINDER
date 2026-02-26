import csv
import os
import uuid
from dotenv import load_dotenv

# Import Couchbase SDK
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from couchbase.options import ClusterTimeoutOptions
from datetime import timedelta

# Load environment variables
load_dotenv()

CSV_FILE = 'PARTS_DATA.csv'

def initialize_couchbase():
    host = os.getenv("COUCHBASE_HOST", "couchbase://10.201.68.111")
    username = os.getenv("COUCHBASE_USERNAME", "webdev")
    password = os.getenv("COUCHBASE_PASSWORD", "webdev123")
    bucket_name = os.getenv("COUCHBASE_BUCKET_NAME", "qgic-gg")
    connect_timeout = int(os.getenv("COUCHBASE_CONNECT_TIMEOUT", "30"))
    query_timeout = int(os.getenv("COUCHBASE_QUERY_TIMEOUT", "10"))
    kv_timeout = int(os.getenv("COUCHBASE_KV_TIMEOUT", "2"))

    auth = PasswordAuthenticator(username, password)
    
    timeout_options = ClusterTimeoutOptions(
        connect_timeout=timedelta(seconds=connect_timeout),
        query_timeout=timedelta(seconds=query_timeout),
        kv_timeout=timedelta(seconds=kv_timeout)
    )
    
    options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

    print(f"Connecting to Couchbase at {host}...")
    try:
        cluster = Cluster(host, options)
        
        # Wait until the cluster is ready for use.
        cluster.wait_until_ready(timedelta(seconds=10))
        
        bucket = cluster.bucket(bucket_name)
        collection = bucket.default_collection()
        print("Connected successfully!")
        return cluster, collection
    except Exception as e:
        print(f"Error connecting to Couchbase: {e}")
        exit(1)

def import_csv_to_couchbase(collection):
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: Cannot find {CSV_FILE}.")
        exit(1)

    print(f"Reading {CSV_FILE}...")
    
    total_count = 0
    
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data = {
                "product_id_pcs": row.get("PRODUCT_ID_PCS", "").strip(),
                "product_id_triad": row.get("PRODUCT_ID_TRIAD", "").strip(),
                "distributor_part_number": row.get("DISTRIBUTOR_PART_NUMBER", "").strip(),
                "alternate_part_number": row.get("ALTERNATE_PART_NUMBER", "").strip()
            }
            
            # Generate a UUID for the document key
            doc_id = str(uuid.uuid4())
            
            try:
                collection.upsert(doc_id, data)
                total_count += 1
                if total_count % 500 == 0:
                    print(f"Uploaded {total_count} records...")
            except CouchbaseException as e:
                print(f"Failed to upsert document {doc_id}: {e}")

    print(f"Import completed successfully! Total uploaded: {total_count}")

if __name__ == "__main__":
    print("Initializing Couchbase SDK...")
    cluster, collection = initialize_couchbase()
    try:
        import_csv_to_couchbase(collection)
    finally:
        cluster.close()
