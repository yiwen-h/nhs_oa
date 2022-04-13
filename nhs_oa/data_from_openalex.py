import os
import requests
import pandas as pd


# if using this package locally please set your own email address as an environmental variable
email_address = os.environ['email_address']

def works_query_from_doi(doi = "10.7861/clinmedicine.19-2-169", email = email_address):
    # accepts a doi and returns a url query string for OpenAlex
    url = f"https://api.openalex.org/works/doi:{doi}?mailto:{email_address}"
    return url

testurl = works_query_from_doi()

def send_request_to_openalex(url = testurl):
    try:
        response = requests.get(url)
        if response.ok:
            metadata = response.json()
            return metadata
    except:
        return f"Error"

testlist = ["10.7861/clinmedicine.19-2-169", "10.21037/cco.2018.11.03",
            "10.1016/j.wneu.2018.11.176", "10.1002/14651858.CD006583.pub5"]

def create_df_from_doilist(doilist = testlist):
    metadata_list = []
    error_list = []
    for doi in doilist:
        url = works_query_from_doi(doi = doi)
        metadata = send_request_to_openalex(url=url)
        if metadata != "Error":
            metadata_list.append(metadata)
        else:
            error_list.append(doi)
    df = pd.DataFrame(metadata_list)
    print(error_list)
    return df

if __name__ == "__main__":
    df = create_df_from_doilist()
    print(df.head())
