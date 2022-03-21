from nhs_oa import get_data

def test_get_pmids():
    pmids = get_data.get_pmids()
    assert isinstance(pmids, list) == True

def test_get_xml():
    art_xml = get_data.get_xml()
    assert art_xml.tag == "PubmedArticleSet"


if __name__ == '__main__':
    test_get_xml()
