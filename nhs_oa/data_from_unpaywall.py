import pandas as pd
import time
import requests
import pickle
import os

email_address = os.environ['email_address']

def get_df(filepath = "csv/2019_crossref_plus_pubmed_test.csv"):
    df = pd.read_csv(filepath, index_col=0)
    return df

test_df = get_df()

def get_info_from_unpaywall(df = test_df, tempsavepath = "csv/test_2019_unpaywall_temp.csv",
                            finalsavepath = "csv/test_2019_unpaywall.csv"):
    start_time = time.ctime()
    all_date_published_upw = []
    all_is_oa = []
    all_oa_status = []
    all_oa_locations = []
    all_genre = []
    errors = []
    for i in range(df.shape[0]):
        doi = df.iloc[i].doi
        url = f"https://api.unpaywall.org/v2/{doi}?email=yiwench@gmail.com"
        try:
            response = requests.get(url)
            metadata = response.json()
            if response.ok == True:
                # get publication date
                pub_date = metadata.get("published_date", "NaN")
                all_date_published_upw.append(pub_date)
                # get is_oa
                is_oa = metadata.get("is_oa", "NaN")
                all_is_oa.append(is_oa)
                # get oa_status
                oa_status = metadata.get("oa_status", "NaN")
                all_oa_status.append(oa_status)
                # get oa_locations
                oa_locations = metadata.get("oa_locations", "NaN")
                all_oa_locations.append(oa_locations)
                # get genre
                genre = metadata.get("genre", "NaN")
                all_genre.append(genre)
                # get missing data if not available through crossref
                if df.iloc[i].journal_title == "NaN":
                    df.iloc[i].journal_title = metadata.get("journal_name", "NaN")
                if df.iloc[i].article_title == "NaN":
                    df.iloc[i].article_title = metadata.get("title", "NaN")
            else:
                all_date_published_upw.append("NaN")
                all_is_oa.append("NaN")
                all_oa_status.append("NaN")
                all_oa_locations.append("NaN")
                all_genre.append("NaN")
        except:
            errors.append([doi])
# save temporary files
        if i % 100 == 0:
            mini_df_dict = {"date_published_upw" : all_date_published_upw,
                            "is_oa" : all_is_oa,
                            "oa_status": all_oa_status,
                            "oa_locations": all_oa_locations,
                            "genre" : all_genre
                            }
            mini_df = pd.DataFrame(mini_df_dict)
            mini_df.to_csv(tempsavepath)
            print(f"{i} / {df.shape[0]} articles metadata obtained from unpaywall")

    unpaywall_df_dict = {"date_published_upw" : all_date_published_upw,
                            "is_oa" : all_is_oa,
                            "oa_status": all_oa_status,
                            "oa_locations": all_oa_locations,
                            "genre" : all_genre
                            }
    unpaywall_df = pd.DataFrame(unpaywall_df_dict)
    unpaywall_df.to_csv(finalsavepath)
    print(f"Finished. Start time: {start_time}. Finish time: {time.ctime()}")
    with open("errors.pkl", "wb") as f:
        pickle.dump(errors, f)
    return unpaywall_df

test_unpaywall_df = get_info_from_unpaywall()

def join_dfs(df1 = test_df, df2 = test_unpaywall_df, savepath = "csv/2019_crossref_pubmed_upw_test.csv"):
    unpaywall_info = df2.copy()
    df1['date_published_upw'] = unpaywall_info.loc[:,"date_published_upw"]
    df1['is_oa'] = unpaywall_info.loc[:,"is_oa"]
    df1['oa_status'] = unpaywall_info.loc[:,"oa_status"]
    df1['oa_locations'] = unpaywall_info.loc[:,"oa_locations"]
    df1['genre'] = unpaywall_info.loc[:,"genre"]
    df1.to_csv(savepath)
    return df1

def get_unpaywall_data_main():
    df = get_df(filepath = "csv/2019_crossref_plus_pubmed.csv")
    unpaywall_df = get_info_from_unpaywall(df = df, tempsavepath = "csv/2019_upw_temp.csv",
                            finalsavepath = "csv/2019_upw.csv")
    with open('errors.pkl', 'rb') as f:
        errors = pickle.load(f)
    print(f"Errors: {errors}")
    full_df = join_dfs(df1 = df, df2 = unpaywall_df, savepath = "csv/2019_crossref_pubmed_upw.csv")
    print(full_df.head())

if __name__ == "__main__":
    get_unpaywall_data_main()
