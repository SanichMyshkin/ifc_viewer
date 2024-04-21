import streamlit as st
from tools import ifchelper
from tools import pandashelper

session = st.session_state


def initialize_session_state():
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False


def load_data():
    if "ifc_file" in session:
        session["DataFrame"] = get_ifc_pandas()
        session.Classes = session.DataFrame["Class"].value_counts(
        ).keys().tolist()
        session["IsDataFrameLoaded"] = True
        session["file_name"] = "example.ifc"


def get_ifc_pandas():
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session.ifc_file,
        "IfcBuildingElement"
    )
    frame = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return frame


def download_excel():
    pandashelper.download_excel(session.file_name, session.DataFrame)


def execute():
    st.header("Таблица данных")
    if not "IsDataFrameLoaded" in session:
        initialize_session_state()
    if not session.IsDataFrameLoaded:
        load_data()
    if session.IsDataFrameLoaded:
        st.write(session.DataFrame)
        st.button("Сохранить *xlsx", key="download_excel",
                  on_click=download_excel)
    else:
        st.header("Загрузите модель для работы с данными")


execute()
