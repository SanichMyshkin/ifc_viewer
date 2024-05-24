import streamlit as st
import pandas as pd


def get_area(dataframe):
    slab_area_columns = [
        column for column in dataframe.columns if 'Slab' in column and 'Area' in column]
    if not slab_area_columns:
        st.error(
            "Данные о площади не доступны. Возможно, вы используете старую версию IFC")
        st.warning('Для корректной работы рекомендуется использовать схемы IFC4')
        return None
    sum_by_level = dataframe.groupby('Level').agg(
        {column: lambda x: round(x.sum(), 3) for column in slab_area_columns}).reset_index()
    sum_by_level_sorted = sum_by_level.sort_values(
        by='Level', key=lambda x: pd.to_numeric(x, errors='coerce'))
    sum_by_level_sorted.index = range(1, len(sum_by_level_sorted) + 1)
    for column in slab_area_columns:
        sum_by_level_sorted[column] = sum_by_level_sorted[column].astype(
            str) + ' м²'
    return sum_by_level_sorted


def sum_area(area_dataframe):
    if area_dataframe is not None:
        clean_dataframe = area_dataframe.copy()
        for column in clean_dataframe.columns:
            if column != 'Level':
                clean_dataframe[column] = clean_dataframe[column].replace(
                    ' м²', '', regex=True).astype(float)

        sums = clean_dataframe.drop(columns=['Level']).sum()
        sums = sums.round(3)
        result = pd.DataFrame(sums).transpose()

        result = result.applymap(lambda x: str(x) + ' м²')

        return result
