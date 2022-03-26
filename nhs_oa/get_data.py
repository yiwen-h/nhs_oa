"""
Downloads data from NCBI Pubmed using Entrez API
"""

import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time

pubmed_api_key = os.environ['pubmed_api_key']
email_address = os.environ['email_address']

# Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/#chapter1.Downloading_Full_Records

def get_pmids(year = '2020', retmax = '5'):
    # returns a list of PMIDs for a given search string
    base_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=nhs%5Baffiliation%5D+AND+{year}%5Bpdat%5D&retmax={retmax}&retmode=json"
    re = requests.get(base_url).json()
    result = re["esearchresult"]["idlist"]
    return result

def get_xml(pmid = '34987726', api=True):
    # returns xml for pubmed article, given a specific pmid
    if api==False:
        url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={pmid}"
    else:
        url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={pmid}&api_key={pubmed_api_key}"
    re = requests.get(url, stream =True)
    re_xml = ET.fromstring(re.content)
    return re_xml

pmid_xml_test = get_xml(pmid = '34987726')

def get_doi(pmid_xml = pmid_xml_test):
    # returns doi for a pubmed article. if doi is not found returns None
    all_article_ids = pmid_xml[0][1][2]
    doi = None
    for i in all_article_ids:
        if i.get('IdType') == "doi":
            doi = i.text
    return doi

def get_article_title(pmid_xml = pmid_xml_test):
    # returns title of article using XML from pubmed
    medline_citation = pmid_xml[0][0]
    article_title = None
    article = medline_citation.find("Article")
    if article:
        article_title = article.find("ArticleTitle").text
    return article_title

def get_year(pmid_xml = pmid_xml_test):
    # returns publication year and month of article using XML from pubmed
    medline_citation = pmid_xml[0][0]
    article = medline_citation.find("Article")
    if article:
        article_date = article.find("ArticleDate")
        if article_date:
            publication_date = f'{article_date.find("Year").text}-{article_date.find("Month").text}'
        else:
            publication_date = None
    else:
        publication_date = None
    return publication_date

def get_orgs(pmid_xml = pmid_xml_test):
    # returns list of organisations for authors
    medline_citation = pmid_xml[0][0]
    article = medline_citation.find("Article")
    author_list = []
    if article:
        author_list = article.find("AuthorList")
    org_list = []
    for i in author_list:
        affiliationinfo = i.find("AffiliationInfo")
        if affiliationinfo:
            affiliation = affiliationinfo.find("Affiliation").text
            affiliation_as_list = affiliation.split(',')
            for phrase in affiliation_as_list:
                if 'Hospital' in phrase or 'NHS' in phrase:
                    org_list.append(phrase.strip())
    return org_list

def get_authors(pmid_xml = pmid_xml_test):
    # returns authors of article using XML from pubmed
    medline_citation = pmid_xml[0][0]
    article = medline_citation.find("Article")
    author_list = []
    if article:
        author_list = article.find("AuthorList")
    if len(author_list) > 3:
        try:
            author_names = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}. et al'
        except:
            author_names = None
    elif len(author_list) == 3:
        try:
            author_1 = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}.'
            author_2 = f'{author_list[1].find("LastName").text}, {author_list[1].find("Initials").text}.'
            author_3 = f'{author_list[2].find("LastName").text}, {author_list[2].find("Initials").text}.'
            author_names = f"{author_1}, {author_2}, & {author_3}"
        except:
            author_names = None
    elif len(author_list) == 2:
        try:
            author_1 = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}.'
            author_2 = f'{author_list[1].find("LastName").text}, {author_list[1].find("Initials").text}.'
            author_names = f"{author_1} & {author_2}"
        except:
            author_names = None
    elif len(author_list) == 1:
        try:
            author_names = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}.'
        except:
            author_names = None
    else:
        author_names = None
    return author_names

def get_unpaywall_json(doi="10.1007/s43465-021-00465-8"):
    url = f"https://api.unpaywall.org/v2/{doi}?email={email_address}"
    response = requests.get(url)
    if response.status_code == 200:
        unpaywall_json = response.json()
    else:
        unpaywall_json = None
    return unpaywall_json

def get_full_info(pmids = ['34987726', '17284678']):
    # returns pandas dataframe containing metadata for each pubmed article searched for
    all_articles = []
    total = len(pmids)
    count = 1
    for pmid in pmids:
        start_time = time.time()
        article_metadata = {'PMID' : pmid}
        print(f"processing article {count}/{total} with PMID {pmid}")
        pmid_xml = get_xml(pmid = pmid)
        # get doi, article title, authors, and year from pubmed
        doi = get_doi(pmid_xml)
        article_metadata['doi'] = doi
        article_title = get_article_title(pmid_xml)
        article_metadata['article_title'] = article_title
        article_authors = get_authors(pmid_xml)
        article_metadata['authors'] = article_authors
        article_pubdate = get_year(pmid_xml)
        article_metadata['pub_date'] = article_pubdate
        article_orgs = get_orgs(pmid_xml)
        article_metadata['authors_nhs_affils'] = article_orgs
        all_articles.append(article_metadata)
        count += 1
        print(f"Process took {time.time() - start_time} seconds")
    articles_df = pd.DataFrame(all_articles)
    return articles_df

def get_unpaywall_info(doi):
    # expand dataframe of info to get journal publisher and oa status from unpaywall
    unpaywall_json = get_unpaywall_json(doi = doi)
    d = {}
    if unpaywall_json is not None:
        d['journal_title'] = unpaywall_json.get("journal_name", None)
        d['journal_publisher'] = unpaywall_json.get("publisher", None)
        d['is_oa'] = unpaywall_json.get("is_oa", None)
        d['oa_status'] = unpaywall_json.get("oa_status", None)
    return unpaywall_json, d

def get_df_as_csv(year = "2020"):
    pmids = get_pmids(year = year, retmax = '40000')
    print(f"Processing {len(pmids)} articles from {year}")
    articles_df = get_full_info(pmids = pmids)
    articles_df.to_csv(f"articles_{year}")


if __name__ == '__main__':
    yearlist = ["2019"]
    for y in yearlist:
        get_df_as_csv(year = y)
