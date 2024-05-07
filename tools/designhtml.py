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
