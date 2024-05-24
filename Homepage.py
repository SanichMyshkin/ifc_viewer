import streamlit as st
from st_pages import Page, show_pages
import ifcopenshell

from tools.designHtml import get_browse_button, get_footer


def configure_page():
    show_pages([Page("Homepage.py", "Главная")])
    st.set_page_config(layout="wide")


def handle_file_upload():
    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file:
        st.session_state["file_name"] = uploaded_file.name
        try:
            array_buffer = uploaded_file.getvalue()
            st.session_state["array_buffer"] = array_buffer
            decoded_content = array_buffer.decode("utf-8")

            st.session_state["ifc_file"] = ifcopenshell.file.from_string(
                decoded_content)
            st.session_state["is_file_loaded"] = True
            st.session_state.update({
                "DataFrame": None,
                "Classes": [],
                "IsDataFrameLoaded": False
            })
            st.success("Файл обработан! Можете начинать работу :)")
        except UnicodeDecodeError:
            st.error("Не удалось декодировать файл. Проверьте кодировку.")
    else:
        st.error("Файл не загружен.")


def render_main_page():
    st.write(get_browse_button(), unsafe_allow_html=True)
    st.write(get_footer(), unsafe_allow_html=True)


def main():
    configure_page()
    st.header('Web IFC-Viewer - приложение для визуализации и анализа ЦИМ')
    render_main_page()

    st.file_uploader(
        label="Загрузить файл",
        type=['ifc'],
        key="uploaded_file",
        on_change=handle_file_upload,
        label_visibility='collapsed'
    )

    if st.session_state.get("is_file_loaded"):
        show_pages(
            [
                Page("Homepage.py", "Главная"),
                Page("pages/Viewer.py", 'Отображение'),
                Page("pages/Tree.py", "Данные модели"),
            ]
        )


if __name__ == "__main__":
    main()
