"""
Downloads data from NCBI Pubmed
"""

import bs4
import requests


# Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/#chapter1.Downloading_Full_Records
year = 2020
base_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=nhs%5Baffiliation%5D+AND+{year}%5Bpdat%5D&retmax=50000&retmode=json"

def get_pmids():
    re = requests.get(base_url).json()
    result = re["esearchresult"]["idlist"]
    return result




if __name__ == '__main__':
    print(get_pmids())
