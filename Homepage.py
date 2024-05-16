import streamlit as st
from st_pages import Page, show_pages
import ifcopenshell

from tools.designhtml import get_browse_button, get_footer


def set_page_configuration():
    show_pages([Page("Homepage.py", "Главная")])
    st.set_page_config(layout="wide")


def callback_upload():
    if "uploaded_file" in st.session_state and st.session_state["uploaded_file"] is not None:
        st.session_state["file_name"] = st.session_state["uploaded_file"].name
        st.session_state["array_buffer"] = st.session_state["uploaded_file"].getvalue(
        )
        st.session_state["ifc_file"] = ifcopenshell.file.from_string(
            st.session_state["array_buffer"].decode("utf-8"))

        st.session_state["is_file_loaded"] = True
        st.session_state["DataFrame"] = None
        st.session_state["Classes"] = []
        st.session_state["IsDataFrameLoaded"] = False
        st.success("Файл обратботан! Можете начинать работу :)")
    else:
        st.error("Файл не загружен.")


def design_main_page():
    browse_button = get_browse_button()
    footer_html = get_footer()
    st.write(browse_button, unsafe_allow_html=True)
    st.write(footer_html, unsafe_allow_html=True)


def main():
    set_page_configuration()
    st.markdown(
        '''
        ### Web IFC-Viewer - приложение для виузализации и анализа ЦИМ
        '''
    )

    design_main_page()

    st.file_uploader(
        label="Ненужный текст, что бы не ругалась консоль",
        type=['ifc'], key="uploaded_file",
        on_change=callback_upload, label_visibility='collapsed')

    if "is_file_loaded" in st.session_state and st.session_state["is_file_loaded"]:
        show_pages(
            [
                Page("Homepage.py", "Главная"),
                Page("pages/Viewer.py", 'Отображение'),
                Page("pages/Tree.py", "Данные модели"),
            ]
        )


if __name__ == "__main__":
    main()
