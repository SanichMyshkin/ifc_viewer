import streamlit as st
import pandas as pd
from pathlib import Path
from tools import ifcdataparse
import matplotlib.pyplot as plt
import seaborn as sns

CLASS = "Class"
LEVEL = "Level"


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
        st.session_state["file_name"] = "example.ifc"


def get_ifc_pandas():
    data, pset_attributes = ifcdataparse.get_objects_data_by_class(
        st.session_state.ifc_file, "IfcBuildingElement")
    dataframe = ifcdataparse.create_pandas_dataframe(data, pset_attributes)
    classes = dataframe["Class"].value_counts().keys().tolist()
    return dataframe, classes


def download_excel(file_name, dataframe):
    file_name = file_name.replace('.ifc', '.xlsx')
    project_root = Path(__file__).resolve().parent.parent
    full_path = project_root / file_name
    writer = pd.ExcelWriter(full_path, engine="xlsxwriter")
    for object_class in dataframe[CLASS].unique():
        df_class = dataframe[dataframe[CLASS] ==
                             object_class]
        non_null_columns = df_class.columns[df_class.notna().any()]
        df_class = df_class[non_null_columns]
        df_class.to_excel(writer, sheet_name=object_class)
    writer.close()
    st.success(f"Файл успешно сохранен по пути: {full_path}")


def get_area(dataframe):
    if 'Qto_SlabBaseQuantities.GrossArea' not in dataframe.columns or 'Qto_SlabBaseQuantities.NetArea' not in dataframe.columns:
        st.error(
            "Данные о площади не доступны. Возможно, вы используете старую версию IFC.")
        return None

    sum_by_level = dataframe.groupby('Level').agg(
        {'Qto_SlabBaseQuantities.GrossArea': 'sum', 'Qto_SlabBaseQuantities.NetArea': 'sum'}).reset_index()
    sum_by_level = sum_by_level.rename(columns={
                                       'Level': 'Этаж', 'Qto_SlabBaseQuantities.GrossArea': 'Общая площадь', 'Qto_SlabBaseQuantities.NetArea': 'Жилая площадь'})
    total_area = sum_by_level['Общая площадь'].sum()
    total_net_area = sum_by_level['Жилая площадь'].sum()
    total_row = pd.DataFrame({"Этаж": ["Суммарная площадь"], "Общая площадь": [
                             total_area], "Жилая площадь": [total_net_area]})
    sum_by_level = pd.concat([sum_by_level, total_row])
    sum_by_level.index = sum_by_level.index + 1
    sum_by_level.loc[len(sum_by_level)] = sum_by_level.sum(numeric_only=True)
    sum_by_level.iloc[-1, 0] = "Сумма"
    return sum_by_level


def display_dataframe(dataframe):
    dataframe = dataframe.dropna(axis=1, how="all")
    st.write(dataframe)


def save_excel_for_class(name, dataframe):
    download_excel(
        f"{name}_{st.session_state['file_name']}",
        dataframe)


def plot_doors_count(dataframe):
    doors_count = dataframe[dataframe['Class'] == 'IfcDoor'].groupby('Level')[
        'Class'].count().reset_index()

    # Set style
    sns.set_style("whitegrid")

    # Create plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='Level', y='Class', data=doors_count, palette="Blues")

    # Customize plot
    ax.set_title('Количество дверей на каждом этаже', fontsize=16)
    ax.set_xlabel('Этаж', fontsize=14)
    ax.set_ylabel('Количество дверей', fontsize=14)
    ax.tick_params(axis='x', labelsize=12, rotation=45)
    ax.tick_params(axis='y', labelsize=12)

    # Add data labels
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center',
                    fontsize=12, color='black',
                    xytext=(0, 5),
                    textcoords='offset points')

    st.pyplot(plt.gcf())  # Display the current figure


def execute():
    st.sidebar.title("Навигация")
    app_mode = st.sidebar.radio("Выберите страницу",
                                ["Таблица данных",
                                 "Площадь по этажам",
                                 "Статистика"])

    if app_mode == "Таблица данных":
        st.header("Таблица данных")
        if not "IsDataFrameLoaded" in st.session_state:
            initialize_session_state()
        if not st.session_state.IsDataFrameLoaded:
            load_data()
        if st.session_state.IsDataFrameLoaded:
            dataframe = st.session_state["DataFrame"]
            st.subheader("Общая таблица данных")
            display_dataframe(dataframe)
            if st.button("Сохранить *xlsx для общей таблицы",
                         key="download_excel_all"):
                download_excel(st.session_state["file_name"], dataframe)
            names_of_classes = dataframe['Class']
            unique_names = names_of_classes.unique()
            for name in unique_names:
                st.subheader(f"Данные класса: {name}")
                class_dataframe = dataframe[dataframe['Class'] == name]
                display_dataframe(class_dataframe)
                if st.button(f"Сохранить *xlsx для класса {name}",
                             key=f"download_excel_{name}"):
                    save_excel_for_class(name, class_dataframe)
        else:
            st.header("Загрузите модель для работы с данными")
    elif app_mode == "Площадь по этажам":
        st.header("Площадь по этажам")
        if not "IsDataFrameLoaded" in st.session_state:
            initialize_session_state()
        if not st.session_state.IsDataFrameLoaded:
            load_data()
        if st.session_state.IsDataFrameLoaded:
            dataframe = st.session_state["DataFrame"]
            area_dataframe = get_area(dataframe)
            if area_dataframe is not None:
                area_dataframe = area_dataframe.iloc[:-1]
                st.write(area_dataframe)
        else:
            st.header("Загрузите модель для работы с данными")
    elif app_mode == "Статистика":
        st.header("Статистика")
        if not "IsDataFrameLoaded" in st.session_state:
            initialize_session_state()
        if not st.session_state.IsDataFrameLoaded:
            load_data()
        if st.session_state.IsDataFrameLoaded:
            dataframe = st.session_state["DataFrame"]
            plot_doors_count(dataframe)
        else:
            st.header("Загрузите модель для работы с данными")


execute()
