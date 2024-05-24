import streamlit as st
from tools.ifcProperties import select_quantity, show_graph, \
    plot_element_distribution
from tools.ifcArea import get_area, sum_area
from tools.ifcTableSet import load_data, show_dataframe, download_as_excel


session_state = st.session_state


def initialize_session():
    session_state["data_frame"] = None
    session_state["Classes"] = []
    session_state["is_data_frame_loaded"] = False


def load_ifc_data():
    if "ifc_file" in session_state:
        dataframe, classes = load_data()
        session_state["data_frame"] = dataframe
        session_state["Classes"] = classes
        session_state["is_data_frame_loaded"] = True


def show_data_table():
    if session_state.is_data_frame_loaded:
        dataframe = session_state["data_frame"]
        st.subheader("Данные")
        tabs = st.tabs(["Общая таблица"] + list(dataframe['Class'].unique()))

        with tabs[0]:
            st.subheader("Общая таблица данных")
            show_dataframe(dataframe)
            st.download_button(
                label="Скачать файл Excel",
                data=download_as_excel(dataframe),
                file_name='AllData.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        for i, class_name in enumerate(dataframe['Class'].unique(), start=1):
            with tabs[i]:
                st.subheader(f"Данные класса: {class_name}")
                class_dataframe = dataframe[dataframe['Class'] == class_name]
                show_dataframe(class_dataframe)
                st.download_button(
                    label=f"Скачать файл Excel класса {class_name}",
                    data=download_as_excel(class_dataframe),
                    file_name=f'{class_name}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    else:
        st.error("Загрузите модель для работы с данными")


def show_area_by_level():
    if session_state.is_data_frame_loaded:
        dataframe = session_state["data_frame"]
        area_dataframe = get_area(dataframe)
        total_area = sum_area(area_dataframe)
        if area_dataframe is not None:
            st.subheader("Площадь по этажам")
            st.dataframe(area_dataframe, hide_index=True)
            st.subheader('Суммарная площадь')
            st.dataframe(total_area, hide_index=True)
    else:
        st.error("Загрузите модель для работы с данными")


def show_statistics():
    if session_state.is_data_frame_loaded:
        dataframe = session_state["data_frame"]
        tabs = st.tabs(["Площадь", 'Статистика', 'График элементов'])
        with tabs[0]:
            show_area_by_level()
        with tabs[1]:
            select_quantity()
            show_graph()
        with tabs[2]:
            plot_element_distribution(dataframe)
    else:
        st.error("Загрузите модель для работы с данными")


def main():
    initialize_session()
    load_ifc_data()
    st.sidebar.title("Навигация")
    app_mode = st.sidebar.radio(
        "Выберите страницу", ["Таблицы данных", "Статистика"])

    if app_mode == "Таблицы данных":
        show_data_table()
    elif app_mode == "Статистика":
        show_statistics()


main()
