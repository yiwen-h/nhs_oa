from nhs_oa import data_from_pubmed

def test_read_txt():
    test_bib_info_str = data_from_pubmed.read_txt()
    assert type(test_bib_info_str) == "str"

def test_txt_to_list():
    test_list = data_from_pubmed.txt_to_list()
    assert type(test_list) == list
    return test_list


def test_get_pmid():
    test_list = test_txt_to_list()
    pmids = data_from_pubmed.get_pmid()
    assert len(pmids) == len(test_list)
