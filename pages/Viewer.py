import streamlit as st
from tools import ifchelper
import json
from pathlib import Path
# from re import L
from typing import Optional
import streamlit.components.v1 as components


frontend_dir = (Path(__file__).parent / "frontend-viewer").absolute()
_component_func = components.declare_component(
    "ifc_js_viewer", path=str(frontend_dir)
)


def ifc_js_viewer(
    url: Optional[str] = None,
):
    component_value = _component_func(
        url=url,
    )
    return component_value


def draw_3d_viewer():
    def get_current_ifc_file():
        return session.array_buffer

    if "ifc_js_response" not in session:
        session["ifc_js_response"] = ""
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())
    st.sidebar.success("Загрузка модели успешна")


def get_psets_from_ifc_js():
    if session.ifc_js_response:
        return json.loads(session.ifc_js_response)


def format_ifc_js_psets(psets):
    return ifchelper.format_ifcjs_psets(psets)


def write_pset_data():
    psets_JSON = get_psets_from_ifc_js()
    if psets_JSON:
        psets = format_ifc_js_psets(psets_JSON)
        for pset in psets.values():
            st.subheader(pset["Name"])
            st.table(pset["Data"])
    else:
        st.text("Ошибка, отутсвуют настройки")


session = st.session_state


def execute():
    st.header("Отображениие Модели")
    if "ifc_file" in session and session["ifc_file"]:
        draw_3d_viewer()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Тут должный будут отображаться данные при клике')
            write_pset_data()
    else:
        st.header("Загрузите файл на главной странице")


execute()
