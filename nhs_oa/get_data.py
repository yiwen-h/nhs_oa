"""
Downloads data from NCBI Pubmed
"""

import bs4
import requests


# Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/#chapter1.Downloading_Full_Records

def get_pmids(year = '2020', retmax = '20'):
    """returns a list of PMIDs for a given search string"""
    base_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=nhs%5Baffiliation%5D+AND+{year}%5Bpdat%5D&retmax={retmax}&retmode=json"
    re = requests.get(base_url).json()
    result = re["esearchresult"]["idlist"]
    return result

def get_full_info(pmids):
    pass



if __name__ == '__main__':
    print(get_pmids())
