"""
Downloads data from NCBI Pubmed
"""

import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd

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
    for i in all_article_ids:
        if i.get('IdType') == "doi":
            return i.text

def get_article_title(pmid_xml = pmid_xml_test):
    # returns title of article using XML from pubmed
    medline_citation = pmid_xml[0][0]
    article = medline_citation.find("Article")
    article_title = article.find("ArticleTitle").text
    return article_title

def get_year(pmid_xml = pmid_xml_test):
    # returns publication year and month of article using XML from pubmed
    medline_citation = pmid_xml[0][0]
    article = medline_citation.find("Article")
    article_date = article.find("ArticleDate")
    publication_date = f'{article_date.find("Year").text}-{article_date.find("Month").text}'
    return publication_date

def get_authors(pmid_xml = pmid_xml_test):
    # returns authors of article using XML from pubmed
    medline_citation = pmid_xml[0][0]
    article = medline_citation.find("Article")
    author_list = article.find("AuthorList")
    if len(author_list) > 3:
        author_names = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}. et al'
    elif len(author_list) == 3:
        author_1 = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}.'
        author_2 = f'{author_list[1].find("LastName").text}, {author_list[1].find("Initials").text}.'
        author_3 = f'{author_list[2].find("LastName").text}, {author_list[2].find("Initials").text}.'
        author_names = f"{author_1}, {author_2}, & {author_3}"
    elif len(author_list) == 2:
        author_1 = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}.'
        author_2 = f'{author_list[1].find("LastName").text}, {author_list[1].find("Initials").text}.'
        author_names = f"{author_1} & {author_2}"
    elif len(author_list) == 1:
        author_names = f'{author_list[0].find("LastName").text}, {author_list[0].find("Initials").text}.'
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
    for pmid in pmids:
        article_metadata = {'PMID' : pmid}
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
        # get journal publisher and oa status from unpaywall
        unpaywall_json = get_unpaywall_json(doi = doi)
        if unpaywall_json is not None:
            article_metadata['journal_title'] = unpaywall_json.get("journal_name", None)
            article_metadata['journal_publisher'] = unpaywall_json.get("publisher", None)
            article_metadata['is_oa'] = unpaywall_json.get("is_oa", None)
            article_metadata['oa_status'] = unpaywall_json.get("oa_status", None)
        all_articles.append(article_metadata)
    articles_df = pd.DataFrame(all_articles)
    return articles_df


if __name__ == '__main__':
    article_metadata = get_full_info()
    print(article_metadata)
