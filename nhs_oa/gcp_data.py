from google.cloud import storage
import json

def get_data_from_gcp():
    client = storage.Client()
    bucket = client.bucket("nhs-oa")
    blob = bucket.blob("unpaywall-data/unpaywall_snapshot_2022-03-09T083001.jsonl.gz")
    full_data = json.load(blob)
    print(full_data[0])
