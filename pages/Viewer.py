import streamlit as st
import json
from pathlib import Path
import streamlit.components.v1 as components
import urllib.parse

from tools.ifcData import fetch_ifc_element_data
from tools.designHtml import hotkey_description

cache = st.session_state


models_dir = (Path(__file__).parent / "models").absolute()
ifc_js_component = components.declare_component(
    "ifc_js_viewer", path=str(models_dir))


def render_ifc_js_viewer(url=None):
    return ifc_js_component(url=url)


def display_3d_viewer():
    cache.ifc_js_response = render_ifc_js_viewer(get_current_ifc_file())


def get_current_ifc_file():
    return cache.array_buffer


def fetch_psets_from_ifc_js():
    if cache.ifc_js_response:
        decoded_response = urllib.parse.unquote(cache.ifc_js_response)
        return json.loads(decoded_response)


def display_pset_data():
    data = fetch_psets_from_ifc_js()
    if data:
        name, quantities, properties = fetch_ifc_element_data(data)
        st.subheader(f'Наименование: {name}', divider='gray')
        for key, value in quantities.items():
            if value:
                value.pop('id', None)
                st.subheader(key)
                st.table(value)
        for key, value in properties.items():
            if value:
                value.pop('id', None)
                st.subheader(key)
                st.table(value)


def main():
    with st.sidebar:
        with st.expander("Подсказка"):
            st.subheader('Горячие клавиши секущих плоскостей')
            hotkeys = {
                "Ctrl + 1": "Вертикальная",
                "Ctrl + 2": "Горизонтальная",
                "9 и 0": "Управление верт.",
                "- и =": "Управление гориз.",
                "←": "Уменьшение скорости",
                "→": "Увеличение скорости",
            }
            for hotkey, action in hotkeys.items():
                st.markdown(hotkey_description(hotkey, action),
                            unsafe_allow_html=True)

    if "ifc_file" in cache and cache.ifc_file:
        cache.setdefault("ifc_js_response", "")
        project_name = cache.ifc_file.by_type('IfcProject')[0][5]
        st.subheader(project_name)
        display_3d_viewer()
        with st.columns(2)[0]:
            display_pset_data()
    else:
        st.error("Для начала загрузите саму модель на главной странице")



main()
