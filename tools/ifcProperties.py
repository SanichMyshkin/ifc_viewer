import pandas as pd
import streamlit as st
import plotly.express as px

session = st.session_state


def filter_df_by_class(df, class_name):
    return df[df["Class"] == class_name].dropna(axis=1, how="all")


def extract_qset_columns(df):
    return list({col.split(".", 1)[0] for col in df.columns if "Qto" in col})


def extract_quantities(df, qset):
    return [col.split(".", 1)[1] for col in df.columns if qset in col] + ["Count"]


def select_quantity():
    class_selector = st.selectbox(
        "Выберите класс", session["Classes"], key="class_selector")
    session["filtered_df"] = filter_df_by_class(
        session["data_frame"], class_selector)
    qset_columns = extract_qset_columns(session["filtered_df"])

    if qset_columns:
        qset_selector = st.selectbox(
            "Выберите набор свойств", qset_columns, key='qset_selector')
        quantities = extract_quantities(session["filtered_df"], qset_selector)
        existing_quantities = [q for q in quantities if q ==
                               "Count" or f"{qset_selector}.{q}" in session["filtered_df"].columns]

        if existing_quantities:
            st.selectbox("Выберите свойство", existing_quantities,
                         key="quantity_selector")
            st.radio('Сортировать по:', ['Level', 'Name'], key="sort_options")
        else:
            st.warning(
                "Выбранный набор свойств не содержит существующих столбцов!")
    else:
        st.warning("В вашей модели отсутствуют свойства!")


def load_graph():
    dataframe = session["filtered_df"]
    quantity_set = session["qset_selector"]
    quantity = session["quantity_selector"]
    user_option = session["sort_options"]

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

    names_for_chart = 'Name_with_count' if user_option == "Name" else user_option
    figure_pie_chart = px.pie(
        dataframe, names=names_for_chart, values=column_name)
    st.plotly_chart(figure_pie_chart)


def show_graph():
    if session.get("quantity_selector") == "Count":
        total = session["filtered_df"].shape[0]
        df = pd.DataFrame(
            {'Название Класса': [session.class_selector], 'Общее количество': [total]})
        st.write("Данные в табличном виде:")
        st.dataframe(df)
    else:
        st.subheader(f"{session.class_selector} - {session.quantity_selector}")
        load_graph()


def analyze_ifc_attributes(selected_class):
    ifc_model = session.get("ifc_file")

    if not ifc_model or not selected_class:
        return

    def get_attributes(entity):
        return {attr: getattr(entity, attr) for attr in dir(entity) if not attr.startswith('_') and not callable(getattr(entity, attr))}

    elements = ifc_model.by_type(selected_class)
    attribute_stats = {}

    for element in elements:
        attributes = get_attributes(element)
        for attr_name, attr_value in attributes.items():
            if attr_name not in attribute_stats:
                attribute_stats[attr_name] = {'filled': 0, 'empty': 0}
            attribute_stats[attr_name]['filled' if attr_value else 'empty'] += 1

    attribute_stats = {k: v for k,
                       v in attribute_stats.items() if v['filled'] > 0}
    data = [{'Атрибут': k, 'Статус': 'Заполнено', 'Количество': v['filled']} for k, v in attribute_stats.items()] + \
           [{'Атрибут': k, 'Статус': 'Пусто', 'Количество': v['empty']}
               for k, v in attribute_stats.items() if v['empty'] > 0]

    df = pd.DataFrame(data)
    fig = px.bar(df, x='Атрибут', y='Количество', color='Статус', barmode='stack',
                 title=f'Статус заполнения атрибутов для {selected_class} в модели IFC',
                 labels={'Атрибут': 'Атрибуты', 'Количество': 'Количество', 'Статус': 'Статус'})

    fig.update_layout(xaxis={'categoryorder': 'total descending'},
                      xaxis_tickangle=-90, width=1000, height=600)
    st.plotly_chart(fig)
