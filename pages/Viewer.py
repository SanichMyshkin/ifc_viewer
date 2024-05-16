import streamlit as st
import json
from pathlib import Path
import streamlit.components.v1 as components
from tools import ifcdataparse

models_dir = (Path(__file__).parent / "models").absolute()
_component_func = components.declare_component(
    "ifc_js_viewer", path=str(models_dir)
)


def ifc_js_viewer(url=None):
    component_value = _component_func(url=url)
    return component_value


def draw_3d_viewer():
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())


def get_current_ifc_file():
    return session.array_buffer


def get_psets_from_ifc_js():
    if session.ifc_js_response:
        return json.loads(session.ifc_js_response)


def format_ifc_js_psets(data):
    if data is None:
        return {}  # Возвращаем пустой словарь в случае, если data равно None
    return ifcdataparse.format_ifcjs_psets(data)


def write_pset_data():
    data = get_psets_from_ifc_js()
    if data:
        st.subheader("Свойства объекта")
        # psets = format_ifc_js_psets(data['props']) # старая версия
        psets = format_ifc_js_psets(data)
        if psets:
            for pset in psets.values():
                st.subheader(pset["Name"])
                st.table(pset["Data"])
        else:
            st.error('Ошибка, данные не найдены!', icon='🚨')


def execute():
    st.header('Визуализация модели')
    if "ifc_file" in session and session["ifc_file"]:
        if "ifc_js_response" not in session:
            session["ifc_js_response"] = ""
        draw_3d_viewer()
        tab1 = st.columns(2)[0]
        with tab1:
            write_pset_data()

    else:
        st.error("Для начала загрузите саму модель на главной странице")


session = st.session_state
execute()
