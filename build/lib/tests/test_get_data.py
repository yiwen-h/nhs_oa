from nhs_oa import get_data

def test_get_pmids():
    pmids = get_data.get_pmids()
    assert isinstance(pmids, list) == True

def test_get_xml(api=True):
    art_xml = get_data.get_xml()
    assert art_xml.tag == "PubmedArticleSet"

def test_get_doi():
    doi = get_data.get_doi()
    assert doi == "10.1007/s43465-021-00465-8"

def test_get_full_info():
    full_info = get_data.get_full_info()
    assert type(full_info) == list and type(full_info[0] == dict)

def test_get_unpaywall_json():
    unpaywall_json = get_data.get_unpaywall_json()
    assert unpaywall_json['title'] == 'There is No Link Between Birth Weight and Developmental Dysplasia of the Hip'

if __name__ == '__main__':
    test_get_unpaywall_json()