import pandas as pd
import streamlit as st
import plotly.express as px

cache = st.session_state


def filter_df_by_class(df, class_name):
    return df[df["Class"] == class_name].dropna(axis=1, how="all")


def extract_qset_columns(df):
    return list({col.split(".", 1)[0] for col in df.columns if "Qto" in col})


def extract_quantities(df, qset):
    return [col.split(".", 1)[1] for col in df.columns if qset in col] + ["Count"]


def select_quantity():
    class_selector = st.selectbox(
        "Выберите класс", cache["Classes"], key="class_selector")
    cache["filtered_df"] = filter_df_by_class(
        cache["data_frame"], class_selector)
    qset_columns = extract_qset_columns(cache["filtered_df"])

    if qset_columns:
        qset_selector = st.selectbox(
            "Выберите набор свойств", qset_columns, key='qset_selector')
        quantities = extract_quantities(cache["filtered_df"], qset_selector)
        existing_quantities = [q for q in quantities if q ==
                               "Count" or f"{qset_selector}.{q}" in cache["filtered_df"].columns]

        if existing_quantities:
            st.selectbox("Выберите свойство", existing_quantities,
                         key="quantity_selector")
            st.radio('Сортировать по:', ['Level', 'Name'], key="sort_options")
        else:
            st.warning(
                "Выбранный набор свойств не содержит существующих столбцов!")
    else:
        st.warning("В вашей модели отсутствуют свойства!")


def show_attribute_stats(selected_class, show_percentage=False, include_empty=False):
    ifc_model = cache.get("ifc_file")
    if not ifc_model or not selected_class:
        return

    elements = ifc_model.by_type(selected_class)
    attribute_stats, total_attributes, filled_attributes = calculate_attribute_stats(
        elements, include_empty)
    plot_attribute_stats(attribute_stats, f'Статус заполнения атрибутов для {selected_class} в модели IFC' if selected_class !=
                         'IfcRoot' else 'Статус заполнения атрибутов во всех классах модели IFC')

    if show_percentage:
        filled_percentage = (filled_attributes / total_attributes) * \
            100 if total_attributes > 0 else 0
        display_percentage_table(filled_percentage)


def calculate_attribute_stats(elements, include_empty):
    attribute_stats = {}
    total_attributes = 0
    filled_attributes = 0

    for element in elements:
        element_attributes = get_attributes(element)
        if not include_empty and all(value is None or value == '' for value in element_attributes.values()):
            continue
        for attr_name, attr_value in element_attributes.items():
            if attr_name not in attribute_stats:
                attribute_stats[attr_name] = {'filled': 0, 'empty': 0}
            attribute_stats[attr_name]['filled' if attr_value else 'empty'] += 1
            total_attributes += 1
            if attr_value:
                filled_attributes += 1

    return {k: v for k, v in attribute_stats.items() if v['filled'] > 0 or include_empty}, total_attributes, filled_attributes


def get_attributes(entity):
    return {attr: getattr(entity, attr) for attr in dir(entity) if not attr.startswith('_') and not callable(getattr(entity, attr))}


def plot_attribute_stats(attribute_stats, title):
    data = [{'Атрибут': k, 'Статус': 'Заполнено', 'Количество': v['filled']} for k, v in attribute_stats.items()] + \
           [{'Атрибут': k, 'Статус': 'Пусто', 'Количество': v['empty']}
               for k, v in attribute_stats.items() if v['empty'] > 0]

    df = pd.DataFrame(data)
    fig = px.bar(df, x='Атрибут', y='Количество', color='Статус', barmode='stack', title=title,
                 labels={'Атрибут': 'Атрибуты', 'Количество': 'Количество', 'Статус': 'Статус'})

    fig.update_layout(xaxis={'categoryorder': 'total descending'},
                      xaxis_tickangle=-90, width=1000, height=600)
    st.plotly_chart(fig)


def display_percentage_table(filled_percentage):
    percentage_df = pd.DataFrame({
        "Показатель": ["Процент заполненных атрибутов"],
        "Значение": [f"{filled_percentage:.2f}%"]
    })
    st.table(percentage_df)


def load_graph(include_empty):
    dataframe = cache["filtered_df"]
    quantity_set = cache["qset_selector"]
    quantity = cache["quantity_selector"]
    user_option = cache["sort_options"]

    if "Name" not in dataframe.columns:
        st.error("Колонка 'Name' отсутствует в данных.")
        return

    type_counts = dataframe["Name"].value_counts()
    dataframe['Name_with_count'] = dataframe['Name'].apply(
        lambda x: f"{x} [{type_counts[x]} шт.]")

    if quantity == "Count":
        st.error("Count не поддерживается для построения графика.")
        return

    column_name = f"{quantity_set}.{quantity}"
    if column_name not in dataframe.columns:
        st.error(f"Колонка {column_name} отсутствует в данных.")
        return

    if not include_empty:
        dataframe = dataframe[dataframe[column_name] != 0]

    names_for_chart = 'Name_with_count' if user_option == "Name" else user_option
    figure_pie_chart = px.pie(
        dataframe, names=names_for_chart, values=column_name)
    st.plotly_chart(figure_pie_chart)


def show_graph(include_empty=False):
    if cache.get("quantity_selector") == "Count":
        total = cache["filtered_df"].shape[0]
        df = pd.DataFrame(
            {'Название Класса': [cache.class_selector], 'Общее количество': [total]})
        st.write("Данные в табличном виде:")
        st.dataframe(df)
    else:
        st.subheader(f"{cache.class_selector} - {cache.quantity_selector}")
        load_graph(include_empty)
