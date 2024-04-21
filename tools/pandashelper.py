from pathlib import Path
import pandas as pd
import streamlit as st


CLASS = "Class"
LEVEL = "Level"


def download_excel(file_name, dataframe):
    file_name = file_name.replace('.ifc', '.xlsx')
    project_root = Path(__file__).resolve().parent.parent
    full_path = project_root / file_name
    writer = pd.ExcelWriter(full_path, engine="xlsxwriter")
    for object_class in dataframe[CLASS].unique():
        df_class = dataframe[dataframe[CLASS] ==
                             object_class].dropna(axis=1, how="all")
        df_class.to_excel(writer, sheet_name=object_class)
    writer.close()
    st.success(f"Файл успешно сохранен по пути: {full_path}")
