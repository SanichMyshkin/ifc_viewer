import streamlit as st
import pandas as pd
from io import BytesIO
from tools import ifcdataparse
import matplotlib.pyplot as plt
import numpy as np


def initialize_session_state():
    st.session_state["DataFrame"] = None
    st.session_state["Classes"] = []
    st.session_state["IsDataFrameLoaded"] = False


def load_data():
    if "ifc_file" in st.session_state:
        dataframe, classes = get_ifc_pandas()
        st.session_state["DataFrame"] = dataframe
        st.session_state["Classes"] = classes
        st.session_state["IsDataFrameLoaded"] = True


def get_ifc_pandas():
    try:
        data, pset_attributes = ifcdataparse.get_objects_data_by_class(
            st.session_state.ifc_file, "IfcBuildingElement")
        dataframe = ifcdataparse.create_pandas_dataframe(data, pset_attributes)
        classes = dataframe['Class'].value_counts().keys().tolist()
        # st.write(dataframe)
        # st.write(classes)
        return dataframe, classes
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return None, None


def download_excel(dataframe):
    with BytesIO() as temp_file:
        with pd.ExcelWriter(temp_file, engine="xlsxwriter") as writer:
            for object_class in dataframe['Class'].unique():
                df_class = dataframe[dataframe['Class'] == object_class]
                non_null_columns = df_class.columns[df_class.notna().any()]
                df_class = df_class[non_null_columns]
                df_class.to_excel(writer, sheet_name=object_class, index=False)
        return temp_file.getvalue()


def get_area(dataframe):
    slab_area_columns = [
        column for column in dataframe.columns if 'Slab' in column and 'Area' in column]
    if not slab_area_columns:
        st.error(
            "Данные о площади не доступны. Возможно, вы используете старую версию IFC")
        st.warning('Для корректной работы рекомендуеться использовать схемы IFC4')
        return None
    sum_by_level = dataframe.groupby('Level').agg(
        {column: 'sum' for column in slab_area_columns}).reset_index()
    return sum_by_level


def sum_area(area_dataframe):
    if area_dataframe is not None:
        sums = area_dataframe.drop(columns=['Level']).sum()
        result = pd.DataFrame(sums).transpose()
        return result


def display_dataframe(dataframe):
    dataframe = dataframe.dropna(axis=1, how="all")
    st.write(dataframe)


def save_excel_for_class(name, dataframe):
    return download_excel(f"{name}_{st.session_state['file_name']}", dataframe)


def plot_stat(dataframe):
    material_counts = dataframe['Class'].value_counts()
    fig, ax = plt.subplots()
    # Создание градиента цветов
    colors = plt.cm.viridis(np.linspace(0, 1, len(material_counts)))
    ax.bar(material_counts.index, material_counts.values, color=colors)
    ax.set_ylabel('Количество')
    plt.xticks(rotation=45, ha='right')
    for i, val in enumerate(material_counts):
        ax.text(
            i, val, f'{val / material_counts.sum() * 100:.1f}%', ha='center', va='bottom')
    plt.tight_layout()
    st.pyplot(fig)


def display_data_table():
    # st.header("Таблица данных")
    initialize_session_state()
    load_data()
    if st.session_state.IsDataFrameLoaded:
        dataframe = st.session_state["DataFrame"]
        st.subheader("Общая таблица данных")
        display_dataframe(dataframe)
        st.download_button(
            label="Скачать файл Excel",
            data=download_excel(dataframe),
            file_name='AllData.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        names_of_classes = dataframe['Class']
        unique_names = names_of_classes.unique()
        for name in unique_names:
            st.subheader(f"Данные класса: {name}")
            class_dataframe = dataframe[dataframe['Class'] == name]
            display_dataframe(class_dataframe)
            st.download_button(
                label=f"Скачать файл Excel класса {name}",
                data=download_excel(class_dataframe),
                file_name=f'{name}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.error("Загрузите модель для работы с данными")


def display_area_by_level():
    initialize_session_state()
    load_data()
    if st.session_state.IsDataFrameLoaded:
        dataframe = st.session_state["DataFrame"]
        area_dataframe = get_area(dataframe)
        area_of_sum = sum_area(area_dataframe)
        if area_dataframe is not None:
            st.subheader("Площадь по этажам")
            st.write(area_dataframe)
            st.subheader('Суммарная площадь')
            st.write(area_of_sum)

    else:
        st.error("Загрузите модель для работы с данными")


def display_statistics():
    # st.header("Статистика")
    initialize_session_state()
    load_data()
    if st.session_state.IsDataFrameLoaded:
        dataframe = st.session_state["DataFrame"]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Отношение элементов')
            plot_stat(dataframe)
        with col2:
            st.write("Надо подумать")
    else:
        st.error("Загрузите модель для работы с данными")


def execute():
    st.sidebar.title("Навигация")
    app_mode = st.sidebar.radio(
        "Выберите страницу", ["Таблица данных", "Площадь по этажам", "Статистика"])

    if app_mode == "Таблица данных":
        display_data_table()
    elif app_mode == "Площадь по этажам":
        display_area_by_level()
    elif app_mode == "Статистика":
        display_statistics()


execute()
