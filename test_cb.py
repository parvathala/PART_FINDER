import os
import sys
import datetime
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator

def main():
    try:
        auth = PasswordAuthenticator('webdev', 'webdev123')
        cluster = Cluster('couchbase://10.201.68.111', ClusterOptions(authenticator=auth))
        cluster.wait_until_ready(datetime.timedelta(seconds=5))
        
        query = "SELECT product_id_pcs, product_id_triad, distributor_part_number, alternate_part_number FROM `qgic-gg` WHERE product_id_pcs = 'TDI1000106'"
        print(f"Running query: {query}")
        
        result = cluster.query(query)
        rows = list(result)
        print(f"Results: {rows}")
        
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
    main()
