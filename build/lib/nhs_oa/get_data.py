"""
Downloads data from NCBI Pubmed
"""

import requests
import xml.etree.ElementTree as ET
import os

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

def get_unpaywall_json(doi="10.1007/s43465-021-00465-8"):
    url = f"https://api.unpaywall.org/v2/{doi}?email={email_address}"
    unpaywall_json = requests.get(url).json()
    return unpaywall_json

def get_full_info(pmids = ['34987726', '17284678']):
    # returns a list of dictionaries containig metadata for each pubmed article searched for
    all_articles = []
    for pmid in pmids:
        article_metadata = {'PMID' : pmid}
        pmid_xml = get_xml(pmid = pmid)
        doi = get_doi(pmid_xml)
        article_metadata['doi'] = doi
        all_articles.append(article_metadata)
    return all_articles
        # articleidlist = pmarticle.findall('ArticleIdList')
        # print(articleidlist)
        # doi = art_id.attrib['doi']
        # pubmed_data = pmid_xml[0].tag
        #  .get('PubmedData')
        # return art_id
    #     if len(article_ids) >= 1:
    #         for article_id in article_ids:
    #             if article_id.attrib.get("idtype") == "doi":
    #                 art_dict['doi']  = article_id.text
    #     all_articles.append(art_dict)
    # return all_articles



if __name__ == '__main__':
    print(get_unpaywall_json())
