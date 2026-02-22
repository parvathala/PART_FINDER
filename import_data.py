import csv
import json
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Before running this script:
# 1. Generate a new private key from Firebase Console -> Project Settings -> Service Accounts
# 2. Save the JSON file as 'serviceAccountKey.json' in this folder
# 3. pip install firebase-admin

SERVICE_ACCOUNT_FILE = 'serviceAccountKey.json'
CSV_FILE = 'PARTS_DATA.csv'
COLLECTION_NAME = 'parts'

def initialize_firebase():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: Cannot find {SERVICE_ACCOUNT_FILE}.")
        print("Please download it from Firebase Console (Project Settings -> Service Accounts).")
        exit(1)
    
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def import_csv_to_firestore(db):
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: Cannot find {CSV_FILE}.")
        exit(1)

    print(f"Reading {CSV_FILE}...")
    
    batch = db.batch()
    batch_count = 0
    total_count = 0
    
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        # Ensure column headers match our expectation
        expected_columns = ["PRODUCT_ID_PCS", "PRODUCT_ID_TRIAD", "DISTRIBUTOR_PART_NUMBER", "ALTERNATE_PART_NUMBER"]
        
        for row in reader:
            # We convert keys to lowercase for easier querying in JS
            data = {
                "product_id_pcs": row.get("PRODUCT_ID_PCS", "").strip(),
                "product_id_triad": row.get("PRODUCT_ID_TRIAD", "").strip(),
                "distributor_part_number": row.get("DISTRIBUTOR_PART_NUMBER", "").strip(),
                "alternate_part_number": row.get("ALTERNATE_PART_NUMBER", "").strip()
            }
            
            # Use auto-generated document ID
            doc_ref = db.collection(COLLECTION_NAME).document()
            batch.set(doc_ref, data)
            
            batch_count += 1
            total_count += 1
            
            # Firestore batches are limited to 500 operations
            if batch_count == 499:
                batch.commit()
                print(f"Committed batch. Total uploaded: {total_count}")
                batch = db.batch()
                batch_count = 0
                
        # Commit any remaining items
        if batch_count > 0:
            batch.commit()
            print(f"Committed final batch. Total uploaded: {total_count}")

    print("Import completed successfully!")

if __name__ == "__main__":
    print("Initializing Firebase Admin SDK...")
    db = initialize_firebase()
    import_csv_to_firestore(db)
