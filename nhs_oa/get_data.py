"""
Downloads data from NCBI Pubmed
"""

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/#chapter1.Downloading_Full_Records

def get_pmids(year = '2020', retmax = '5'):
    """returns a list of PMIDs for a given search string"""
    base_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=nhs%5Baffiliation%5D+AND+{year}%5Bpdat%5D&retmax={retmax}&retmode=json"
    re = requests.get(base_url).json()
    result = re["esearchresult"]["idlist"]
    return result

def get_xml(pmid = '34987726'):
    url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={pmid}"
    re = requests.get(url, stream =True)
    re_xml = ET.fromstring(re.content)
    return re_xml

def get_full_info(pmids = ['34987726']):
    all_articles = []
    for pmid in pmids:
        url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={pmid}"
        re = requests.get(url, stream =True)
        root = ET.fromstring(re.content)
        art_dict = {}
        article_ids = root.findall('ArticleIdList')
        if len(article_ids) >= 1:
            for article_id in article_ids:
                if article_id.attrib.get("idtype") == "doi":
                    art_dict['doi']  = article_id.text
        all_articles.append(art_dict)
    return all_articles



if __name__ == '__main__':
    print(get_full_info())
