"""
For adding additional metadata using crossref API and doi information.
- date published
- list of authors
- journal title
- article title
- number of times article was cited
- number of times article was referenced
"""

import email
import pandas as pd
import requests
import os

email_address = os.environ['email_address']

def get_df(filepath = "csv/test_data.csv"):
    df = pd.read_csv(filepath, index_col=0)
    return df

df = get_df()

def remove_no_dois(df = df):
    no_doi = df["doi"].notna()
    df = df[no_doi]
    return df

def get_info_from_crossref(df = df):
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
        try:
            response = response.json()
            metadata = response.get('message')
            # get publication date
            date_as_list = metadata.get('published').get('date-parts')[0]
            if len(date_as_list) > 1:
                pub_date = f"{date_as_list[0]}-{date_as_list[1]}"
            else:
                pub_date = f"{date_as_list[0]}"
            all_date_published.append(pub_date)
            # get authors
            author_list = []
            authors_metadata = metadata.get('author')
            for author in authors_metadata:
                author_name = f"{author.get('family')}, {author.get('given')}"
                author_list.append(author_name)
            all_author_list.append(author_list)
            # get journal title
            all_journal_title.append(metadata.get('container-title')[0])
            # get article title
            all_article_title.append(metadata.get('title')[0])
            # get num_citations
            all_num_citations_crossref.append(metadata.get("is-referenced-by-count"))
            # get num_references
            all_num_references_crossref.append(metadata.get("references-count"))
        except:
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
            mini_df.to_csv("csv/2019_crossref_plus_pubmed_temp.csv")
            print(f"{i} / {df.shape[0]} articles metadata obtained from crossref")
    df['date_published'] = all_date_published
    df['authors'] = all_author_list
    df['journal title'] = all_journal_title
    df['article title'] = all_article_title
    df['num_times_cited'] = all_num_citations_crossref
    df['num_references'] = all_num_references_crossref
    df.to_csv("csv/2019_crossref_plus_pubmed_csv")
