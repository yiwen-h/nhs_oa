"""
For adding additional metadata using crossref API and doi information.
- date published
- list of authors
- journal title
- article title
- number of times article was cited
- number of times article was referenced
"""

from distutils.sysconfig import get_config_h_filename
import pandas as pd
import requests
import os
import time

email_address = os.environ['email_address']

def get_df(filepath = "csv/test_data.csv"):
    df = pd.read_csv(filepath, index_col=0)
    return df

test_df = get_df()

def remove_no_dois(df = test_df):
    no_doi = df["doi"].notna()
    df = df[no_doi]
    return df

test_clean_df = remove_no_dois()

def get_info_from_crossref(df = test_clean_df, tempsavepath = "csv/test_2019_crossref_plus_pubmed_temp.csv",
                            finalsavepath = "csv/test_2019_crossref_only.csv"):
    start_time = time.ctime()
    headers = {
        'User-Agent': f'NHS_OA (https://github.com/yiwen-h/nhs_oa/; mailto:{email_address})',
        'From': f'{email_address}'
    }
    all_date_published = []
    all_author_list = []
    all_journal_title = []
    all_article_title = []
    all_num_citations_crossref = []
    all_num_references_crossref = []

    for i in range(df.shape[0]):
        doi = df.iloc[i].doi
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, headers=headers)
        if response.ok == True:
            response = response.json()
            metadata = response.get('message')
            # get publication date
            pub_date = list(metadata.get('published').get('date-parts', "NaN")[0])
            all_date_published.append(pub_date)
            # get authors
            author_list = []
            authors_metadata = metadata.get('author', 'NaN')
            if authors_metadata != 'NaN':
                for author in authors_metadata:
                    author_name = f"{author.get('family', 'NaN')}, {author.get('given', 'NaN')}"
                    author_list.append(author_name)
            all_author_list.append(author_list)
            # get journal title
            all_journal_title.append(metadata.get('container-title', "NaN")[0])
            # get article title
            all_article_title.append(metadata.get('title', "NaN")[0])
            # get num_citations
            all_num_citations_crossref.append(metadata.get("is-referenced-by-count", "NaN"))
            # get num_references
            all_num_references_crossref.append(metadata.get("references-count", "NaN"))
        else:
            all_date_published.append("NaN")
            all_author_list.append(["NaN"])
            all_journal_title.append("NaN")
            all_article_title.append("NaN")
            all_num_citations_crossref.append("NaN")
            all_num_references_crossref.append("NaN")
        if i % 100 == 0:
            mini_df_dict = {"date_published" : all_date_published,
                            "authors" : all_author_list,
                            "journal_title": all_journal_title,
                            "article_title": all_article_title,
                            "all_num_citations_crossref" : all_num_citations_crossref,
                            "all_num_references_crossref" :  all_num_references_crossref
                            }
            mini_df = pd.DataFrame(mini_df_dict)
            mini_df.to_csv(tempsavepath)
            print(f"{i} / {df.shape[0]} articles metadata obtained from crossref")
    crossref_df_dict = {"date_published" : all_date_published,
                            "author_list" : all_author_list,
                            "journal_title": all_journal_title,
                            "article_title": all_article_title,
                            "num_citations_crossref" : all_num_citations_crossref,
                            "num_references_crossref" :  all_num_references_crossref
                            }
    crossref_df = pd.DataFrame(crossref_df_dict)
    crossref_df.to_csv(finalsavepath)
    print(f"Finished. Start time: {start_time}. Finish time: {time.ctime()}")
    return crossref_df

test_crossref_df = get_info_from_crossref()

def join_dfs(df1 = test_df, df2 = test_crossref_df, savepath = "csv/2019_crossref_plus_pubmed_test.csv"):
    crossref_info = df2.copy()
    df1['date_published'] = crossref_info.loc[:,"date_published"]
    df1['author_list'] = crossref_info.loc[:,"author_list"]
    df1['journal title'] = crossref_info.loc[:,"journal_title"]
    df1['article title'] = crossref_info.loc[:,"article_title"]
    df1['num_citations_crossref'] = crossref_info.loc[:,"num_citations_crossref"]
    df1['num_references_crossref'] = crossref_info.loc[:,"num_references_crossref"]
    df1.to_csv(savepath)

if __name__ == "__main__":
    df = get_df(filepath = "csv/2019_pubmed_data_parsed.csv")
    df_clean = remove_no_dois(df = df)
    crossref_df = get_info_from_crossref(df = df_clean, tempsavepath = "csv/2019_crossref_plus_pubmed_temp.csv",
                                            finalsavepath = "csv/2019_crossref_only.csv")
    join_dfs(df1 = df_clean, df2 = crossref_df, savepath = "csv/2019_crossref_plus_pubmed.csv")
