from nhs_oa.get_data import *

def test_get_pmids():
    pmids = get_pmids()
    assert isinstance(pmids, list) == True
