"""
For turning txt files downloaded from Pubmed into a pandas dataframe with key metadata:
- doi
- pmid
- affiliations
- abstract
"""

import pandas as pd
import re


def read_txt(filepath = "nhs_oa/data/example_affils.txt"):
    # reads pubmed abstract txt file and returns python string
    filepath = filepath
    with open(filepath, encoding="utf-8") as f:
        bib_info_str = f.read()
    return bib_info_str

test_bib_info_str = read_txt()

def txt_to_list(bib_info_str = test_bib_info_str):
    # turns python string into python list of articles
    splitter = re.compile("(\\n\\n\\n\d+. )")
    bib_info_list = re.split(splitter, bib_info_str)
    new_list = []
    for i in range(len(bib_info_list)):
        if i % 2 == 0:
            new_list.append(bib_info_list[i])
    return new_list

test_new_list = txt_to_list()

def get_pmid(new_list = test_new_list):
    # returns list of PMIDs extracted from the list of pubmed article abstracts
    pmid_list = []
    pmid_errors = []
    for i in range(len(new_list)):
        pmid_re = re.findall(r"(PMID: )(\d+)", new_list[i])
        if pmid_re:
            pmid = pmid_re[0][1]
            pmid_list.append(pmid)
        else:
            pmid_errors.append(i)
    print(f"Completed. {len(pmid_list)} articles have a PMID. {len(pmid_errors)} do not have a PMID")
    return pmid_list

def get_doi(new_list = test_new_list):
    # returns list of DOIs extracted from the list of pubmed article abstracts
    doi_errors = []
    doi_list = []
    for i in range(len(new_list)):
        doi_re = re.findall(r"(DOI: )(.+)(\n)", new_list[i])
        if doi_re:
            doi = doi_re[0][1]
            doi_list.append(doi)
        else:
            doi_list.append('NaN')
            doi_errors.append(i)
    print(f"Completed. {len(doi_list)} articles have a DOI. {len(doi_errors)} do not have a DOI")
    return doi_list

def get_affiliations(new_list = test_new_list):
    # returns list of affiliations extracted from the list of pubmed article abstracts
    affil_errors = []
    final_affil_list = []
    nums = re.compile("\(\d+\)")
    for i in range(len(new_list)):
        affils = re.findall(r"\n\(\d+\).+\n?.+", new_list[i])
        affils_list = []
        temp_list = []
        if affils:
            for full_affil in affils:
                full_affil_list = list(full_affil.split(","))
                for each in full_affil_list:
                    if ('hospital' in each.lower() or 'nhs' in each.lower()) and "@" not in each.lower():
                        nonums = re.split(nums, each)
                        for numless in nonums:
                            if ('hospital' in numless.lower() or 'nhs' in numless.lower()):
                                temp_list.append(numless)
            for affil in temp_list:
                affils_list.append(affil.replace("\n", "").strip())
            final_affil_list.append(affils_list)
            if affils_list == []:
                affil_errors.append(i)
        else:
            affil_errors.append(i)
    print(f"Completed. {len(final_affil_list)} articles have some affiliation info. {len(affil_errors)} do not have affiliation info")
    return final_affil_list

def get_abstracts(new_list = test_new_list):
    # returns list of abstracts from txt file of pubmed article abstracts
    abstract_list = []
    abstract_errors = []
    for i in range(len(new_list)):
        abstract_plus = re.search(r"(Author information:)(.+)(?:©|PMCID|PMID|DOI)", new_list[i], re.DOTALL)
        if abstract_plus:
            abstract_plus = abstract_plus.group(2)
            m = re.search("\n\n", abstract_plus)
            if m:
                without_affils = abstract_plus[m.end():]
                n = re.search("\n\n", without_affils)
                if n:
                    without_ids = without_affils[:n.start()]
                    abstract = without_ids.replace("\n", "").strip()
                    abstract_list.append(abstract)
                else:
                    abstract_list.append('NaN')
                    abstract_errors.append(i)
            else:
                abstract_list.append('NaN')
                abstract_errors.append(i)
        else:
            abstract_list.append('NaN')
            abstract_errors.append(i)
    print(f"Completed. {len(abstract_list)} articles have an abstract. {len(abstract_errors)} do not have an abstract")
    return abstract_list


test_pmid_list = get_pmid()
test_doi_list = get_doi()
test_affils_list = get_affiliations()
test_abstract_list = get_abstracts()

def create_df(pmid_list = test_pmid_list, doi_list = test_doi_list,
                affils_list = test_affils_list, abstract_list = test_abstract_list):
    info_dict = {"pmid": pmid_list,
                "doi": doi_list,
                "affiliations": affils_list,
                "abstract": abstract_list
                }
    data_df = pd.DataFrame(info_dict)
    return data_df

def main(filepath = f"nhs_oa/data/example_affils.txt", multipage = False, csvpath = "csv/2019_pubmed_data.csv"):
    bib_info_str = read_txt(filepath = filepath)
    new_list = txt_to_list(bib_info_str = bib_info_str)
    pmid_list = get_pmid(new_list)
    doi_list = get_doi(new_list)
    affils_list = get_affiliations(new_list)
    abstract_list = get_abstracts(new_list)
    data_df = create_df(pmid_list = pmid_list, doi_list = doi_list,
                        affils_list = affils_list, abstract_list = abstract_list)
    if multipage == True:
        for i in range(2,5):
            bib_info_str = read_txt(filepath = f"nhs_oa/data/2019abstract-nhsAffilia-set{i}.txt")
            new_list = txt_to_list(bib_info_str = bib_info_str)
            pmid_list = get_pmid(new_list)
            doi_list = get_doi(new_list)
            affils_list = get_affiliations(new_list)
            abstract_list = get_abstracts(new_list)
            temp_df = create_df(pmid_list = pmid_list, doi_list = doi_list,
                                affils_list = affils_list, abstract_list=abstract_list)
            dfs = [data_df, temp_df]
            data_df = pd.concat(dfs,
                        axis=0,
                        join="outer",
                        ignore_index=True,
                        keys=None,
                        levels=None,
                        names=None,
                        verify_integrity=False,
                        copy=True )
    data_df.to_csv(csvpath)

if __name__ == "__main__":
    main(filepath = "nhs_oa/data/2019abstract-nhsAffilia-set1.txt", multipage = True,
            csvpath = "csv/2019_pubmed_data_parsed.csv")
