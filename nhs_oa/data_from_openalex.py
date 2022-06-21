import os
import requests
import pandas as pd
import time
import pickle

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

def get_df(filepath = "csv/2019_crossref_pubmed_upw.csv"):
    df = pd.read_csv(filepath, index_col=0)
    return df

test_df = get_df().iloc[:5]

def get_info_from_openalex(df = test_df, tempsavepath = "csv/test_csv/test_2019_openalex_temp.csv",
                            finalsavepath = "csv/test_csv/test_2019_openalex.csv"):
    start_time = time.ctime()
    openalex_info = []
    errors = []
    for i in range(df.shape[0]):
        doi = df.iloc[i].doi
        url = works_query_from_doi(doi = doi)
        try:
            response = requests.get(url)
            metadata = response.json()
            if response.ok == True:
                openalex_info.append(metadata)
            else:
                openalex_info.append("NaN")
        except:
            errors.append([doi])
# save temporary files
        if i % 100 == 0:
            mini_df_dict = {"openalex_info" : openalex_info,
                            }
            mini_df = pd.DataFrame(mini_df_dict)
            mini_df.to_csv(tempsavepath)
            print(f"{i} / {df.shape[0]} articles metadata obtained from OpenAlex")

    openalex_df_dict = {"openalex_info" : openalex_info,
                            }
    openalex_df = pd.DataFrame(openalex_df_dict)
    openalex_df.to_csv(finalsavepath)
    print(f"Finished. Start time: {start_time}. Finish time: {time.ctime()}")
    with open("openalexerrors.pkl", "wb") as f:
        pickle.dump(errors, f)
    return openalex_df

test_openalex_df = get_info_from_openalex()

def join_dfs(df1 = test_df, df2 = test_openalex_df, savepath = "csv/2019_crossref_pubmed_upw_openalex_test.csv"):
    df1['openalex_metadata'] = df2.loc[:,"openalex_info"]
    df1.to_csv(savepath)
    return df1

def get_openalex_data_main():
    df = get_df(filepath = "csv/2019_crossref_pubmed_upw.csv")
    openalex_df = get_info_from_openalex(df = df, tempsavepath = "csv/2019_openalex_temp.csv",
                            finalsavepath = "csv/2019_openalex.csv")
    with open('openalexerrors.pkl', 'rb') as f:
        errors = pickle.load(f)
    print(f"Errors: {errors}")
    full_df = join_dfs(df1 = df, df2 = openalex_df, savepath = "csv/2019_crossref_pubmed_upw_openalex.csv")
    print(full_df.head())

if __name__ == "__main__":
    get_openalex_data_main()
