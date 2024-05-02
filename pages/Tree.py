import streamlit as st
import pandas as pd
from pathlib import Path
from tools import ifcdataparse

CLASS = "Class"
LEVEL = "Level"


def initialize_session_state():
    st.session_state["DataFrame"] = None
    st.session_state["Classes"] = []
    st.session_state["IsDataFrameLoaded"] = False


def load_data():
    if "ifc_file" in st.session_state:
        dataframe, classes = get_ifc_pandas()
        st.session_state["DataFrame"] = dataframe
        st.session_state["Classes"] = classes
        st.session_state["IsDataFrameLoaded"] = True
        st.session_state["file_name"] = "example.ifc"


def get_ifc_pandas():
    data, pset_attributes = ifcdataparse.get_objects_data_by_class(
        st.session_state.ifc_file, "IfcBuildingElement")
    dataframe = ifcdataparse.create_pandas_dataframe(data, pset_attributes)
    classes = dataframe["Class"].value_counts().keys().tolist()
    return dataframe, classes


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


def execute():
    st.header("Таблица данных")
    if not "IsDataFrameLoaded" in st.session_state:
        initialize_session_state()
    if not st.session_state.IsDataFrameLoaded:
        load_data()
    if st.session_state.IsDataFrameLoaded:
        dataframe = st.session_state["DataFrame"]
        st.subheader("Общая таблица данных")
        st.write(dataframe)

        # Добавляем кнопку для загрузки общей таблицы
        if st.button("Сохранить *xlsx для общей таблицы", key="download_excel_all"):
            download_excel(st.session_state["file_name"], dataframe)

        names_of_classes = dataframe['Class']
        unique_names = names_of_classes.unique()

        # Выводим таблицы для каждого уникального класса
        for name in unique_names:
            st.subheader(f"Данные класса: {name}")
            class_dataframe = dataframe[dataframe['Class'] == name]
            st.write(class_dataframe)

            if st.button(f"Сохранить *xlsx для класса {name}", key=f"download_excel_{name}"):
                download_excel(
                    f"{name}_{st.session_state['file_name']}", class_dataframe)
    else:
        st.header("Загрузите модель для работы с данными")


execute()
