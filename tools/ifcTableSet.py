import streamlit as st
from tools.ifcData import fetch_elements_by_class, create_dataframe
from io import BytesIO
import pandas as pd

cache = st.session_state


def load_data():
    try:
        data, pset_attributes = fetch_elements_by_class(
            cache.ifc_file, "IfcBuildingElement")
        dataframe = create_dataframe(data, pset_attributes)
        classes = dataframe['Class'].value_counts().keys().tolist()
        return dataframe, classes
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return None, None


def download_as_excel(dataframe):
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            for object_class in dataframe['Class'].unique():
                class_df = dataframe[dataframe['Class'] == object_class]
                non_null_columns = class_df.columns[class_df.notna().any()]
                class_df = class_df[non_null_columns]
                class_df.to_excel(writer, sheet_name=object_class, index=False)
        return buffer.getvalue()


def show_dataframe(dataframe):
    cleaned_dataframe = dataframe.dropna(axis=1, how="all")
    st.write(cleaned_dataframe)
