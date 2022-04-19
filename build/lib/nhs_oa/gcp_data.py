from google.cloud import storage
import json
import gcsfs
import gzip
import os

gcloud_auth = os.environ["GOOGLE_APPLICATION_CREDENTIALS_NHSOA"]

def get_data_from_gcp():
    client = storage.Client()
    bucket = client.bucket("nhs-oa-bucket")
    blob = bucket.blob("unpaywall-data-snapshots.s3.us-west-2.amazonaws.com/unpaywall_snapshot_2022-03-09T083001.jsonl.gz")
    full_data = json.load(blob)
    print(full_data[0])

def get_data_from_gcp_2():
    fs = gcsfs.GCSFileSystem(token = gcloud_auth, project='nhs-oa')
    # with fs.open('nhs-oa-bucket/unpaywall-data-snapshots.s3.us-west-2.amazonaws.com/unpaywall_snapshot_2022-03-09T083001.jsonl.gz') as f:
    #     gz = gzip.GzipFile(fileobj=f)
    # file_as_string = fs.read()
    # your_json = json.loads(file_as_string)
    # print(your_json[0])
    data = json.load(gzip.open(fs))
    print(data[0])

if __name__ == "__main__":
    get_data_from_gcp()
