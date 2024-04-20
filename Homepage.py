import streamlit as st
import ifcopenshell


def callback_upload():
    st.session_state['is_file_uploaded'] = True
    st.session_state['array_buffer'] = st.session_state['uploaded_file'].getvalue()
    st.session_state['ifc_file'] = ifcopenshell.file.from_string(
        st.session_state['uploaded_file'].getvalue().decode('utf-8')
    )


def get_project_name():
    return st.session_state['ifc_file'].by_type('IfcProject')[0].Name


def change_project_name():
    st.session_state['ifc_file'].by_type(
        'IfcProject')[0].Name = st.session_state['project_name_input']


def main():
    st.set_page_config(
        layout="wide",
        page_title="IFC Stream",
    )
    uploaded = 'is_file_uploaded'
    st.title("Web IFC Viewer")
    st.markdown(
        '''
        ### Загрузите файл и перейдите на страницу просмотра модели
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
    uploaded_file = st.file_uploader(
        "", key="uploaded_file", on_change=callback_upload)

    if uploaded in st.session_state and st.session_state[uploaded]:
        st.success("File is loaded!")
        col1, col2 = st.columns(2)
        with col1:
            st.write(get_project_name())
        with col2:
            st.text_input("Edit name", key="project_name_input")
            st.button('Apply', key='project_name_apply',
                      on_click=change_project_name)


if __name__ == "__main__":
    main()
