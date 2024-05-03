import streamlit as st
from st_pages import Page, show_pages
import ifcopenshell


def set_page_configuration():
    show_pages([Page("Homepage.py", "Главная")])
    st.set_page_config(layout="wide")


def callback_upload():
    st.session_state['is_file_uploaded'] = True
    st.session_state['array_buffer'] = st.session_state['uploaded_file'].getvalue()
    st.session_state['ifc_file'] = ifcopenshell.file.from_string(
        st.session_state['uploaded_file'].getvalue().decode('utf-8')
    )


def main():
    set_page_configuration()
    uploaded = 'is_file_uploaded'
    st.markdown(
        '''
        ### Web IFC-Viewer - приложение для виузализации и анализа ЦИМ
        '''
    )

    css = '''
    <style>
    [data-testid="stFileUploadDropzone"] div div::before {content:"Загрузите файл"; font-size: 1.2rem}
    [data-testid="stFileUploadDropzone"] div div span{display:none;}
    [data-testid="stFileUploadDropzone"] div div::after {color: grey; font-size: .8em; content:".ifc"}
    [data-testid="stFileUploadDropzone"] div div small{display:none;}
    [data-testid="stFileUploadDropzone"] button{display:none;}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)
    footer_html = """
    <footer style="position: fixed; bottom: 0; width: 100%; background-color: #f8f9fa; text-align: center; padding: 10px;">
        <p style="margin: 0;">ИЦТМС 4-2 Мышкин Александр</p>
    </footer>
    """

    st.markdown(footer_html, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "", key="uploaded_file", on_change=callback_upload)

    if uploaded in st.session_state and st.session_state[uploaded]:
        st.success("Файл обратботан!\nМожете начинать работу :)")
        show_pages(
            [
                Page("Homepage.py", "Главная"),
                Page("pages/Viewer.py", 'Отображение'),
                Page("pages/Tree.py", "Данные модели"),
            ]
        )


if __name__ == "__main__":
    main()
