import streamlit as st
import json
from pathlib import Path
import streamlit.components.v1 as components
from tools import ifcdataparse
import urllib.parse

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
        decoded_response = urllib.parse.unquote(session.ifc_js_response)
        return json.loads(decoded_response)


def write_pset_data():
    data = get_psets_from_ifc_js()
    if data:
        name, qtos, psets = ifcdataparse.get_ifcdata(data)
        st.subheader(f'Наименование: {name}', divider='gray')
        for key, value in qtos.items():
            if value:
                if value.get('id'):
                    value.pop('id')
                st.subheader(key)
                st.table(value)
        for key, value in psets.items():
            if value:
                if value.get('id'):
                    value.pop('id')
                st.subheader(key)
                st.table(value)


def execute():
    if "ifc_file" in session and session["ifc_file"]:
        if "ifc_js_response" not in session:
            session["ifc_js_response"] = ""
        name = st.session_state['ifc_file'].by_type('IfcProject')[0][5]
        st.subheader(name)
        draw_3d_viewer()
        tab1 = st.columns(2)[0]
        with tab1:
            write_pset_data()
    else:
        st.error("Для начала загрузите саму модель на главной странице")


session = st.session_state
execute()
