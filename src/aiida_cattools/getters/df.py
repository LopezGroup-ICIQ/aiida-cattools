import pandas as pd


def get_df_structural_changes(df_in: pd.DataFrame):
    structural_changes = [
        item for sublist in df_in["structural_change"].values for item in sublist
    ]
    return structural_changes
