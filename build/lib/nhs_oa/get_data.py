"""
Downloads data from NCBI Pubmed
"""

import bs4
import requests


# Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/#chapter1.Downloading_Full_Records
base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
params = {'db': 'pubmed',
          'term' : 'asthma[mesh]+AND+leukotrienes[mesh]+AND+2009[pdat]'}

def get_data():
    re = requests.get(base_url, params=params)
    print(re.url)
    print(re.raw)


if __name__ == '__main__':
    print(get_data)
