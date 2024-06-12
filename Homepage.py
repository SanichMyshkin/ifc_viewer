import streamlit as st
from st_pages import Page, show_pages
import ifcopenshell


def get_browse_button():
    return '''
    <style>
        div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"] {
            height: 100px;
        }
        div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"]>button[data-testid="baseButton-secondary"] {
            color:white;
        }
        div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"]>button[data-testid="baseButton-secondary"]::after {
            content: "Выбрать";
            color:black;
            display: block;
            position: absolute;
        }
        div[data-testid="stFileDropzoneInstructions"]>div>span {
            visibility:hidden;
        }
        div[data-testid="stFileDropzoneInstructions"]>div>span::after {
            content:"Перетащите файл сюда";
            visibility:visible;
            display:block;
        }
        div[data-testid="stFileDropzoneInstructions"]>div>small {
            visibility:hidden;
        }
        div[data-testid="stFileDropzoneInstructions"]>div>small::before {
            content:"Максимальный размер 1000 Мб";
            visibility:visible;
            display:block;
        }
    </style>
    '''


def get_footer():
    return """
    <footer style="position: fixed; bottom: 0; width: 100%; background-color: #f8f9fa; text-align: center; padding: 10px;">
        <p style="margin: 0;">ИЦТМС 4-2 Мышкин Александр</p>
    </footer>
    """


def hotkey_description(hotkey, action):
    return f"<b>{hotkey}</b>: {action}"


cache = st.session_state


def configure_page():
    show_pages([Page("Homepage.py", "Главная")])
    st.set_page_config(layout="wide")


def handle_file_upload():
    uploaded_file = cache.get("uploaded_file")
    if uploaded_file:
        cache["file_name"] = uploaded_file.name
        try:
            array_buffer = uploaded_file.getvalue()
            cache["array_buffer"] = array_buffer
            decoded_content = array_buffer.decode("utf-8")

            cache["ifc_file"] = ifcopenshell.file.from_string(
                decoded_content)
            cache["is_file_loaded"] = True
            cache.update({
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

    if cache.get("is_file_loaded"):
        show_pages(
            [
                Page("Homepage.py", "Главная"),
                Page("pages/Viewer.py", 'Отображение'),
                Page("pages/Tree.py", "Данные модели"),
            ]
        )


if __name__ == "__main__":
    main()
