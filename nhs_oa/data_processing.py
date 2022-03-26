import pandas as pd
import requests

def get_df():
    for i in range(1,5):
        sub_df = pd.read_csv(f"data/2019csv-nhsAffilia-set{i}.csv")
    pass
