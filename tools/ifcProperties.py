import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

session = st.session_state


def filter_df_by_class(df, class_name):
    return df[df["Class"] == class_name].dropna(axis=1, how="all")


def extract_qset_columns(df):
    return list({col.split(".", 1)[0] for col in df.columns if "Qto" in col}) or None


def extract_quantities(df, qset):
    return [col.split(".", 1)[1] for col in df.columns if qset in col] + ["Count"]


def select_quantity():
    st.selectbox("Выберите класс", session["Classes"], key="class_selector")
    session["filtered_df"] = filter_df_by_class(
        session["data_frame"], session["class_selector"])
    # st.write(session['data_frame'])
    session["qset_columns"] = extract_qset_columns(session["filtered_df"])

    if session["qset_columns"] is not None:
        st.selectbox("Выберите набор свойств",
                     session["qset_columns"], key='qset_selector')
        quantities = extract_quantities(
            session["filtered_df"], session["qset_selector"])

        existing_quantities = [q for q in quantities if q ==
                               "Count" or f"{session.qset_selector}.{q}" in session["filtered_df"].columns]

        if existing_quantities:
            st.selectbox("Выберите свойство", existing_quantities,
                         key="quantity_selector")
            st.radio('Сортировать по:', ['Level', 'Type'], key="sort_options")
        else:
            st.warning(
                "Выбранный набор свойств не содержит существующих столбцов!")
    else:
        st.warning("В вашей модели отсутствуют свойства!")


def load_graph(dataframe, quantity_set, quantity, user_option):
    if quantity != "Count":
        column_name = f"{quantity_set}.{quantity}"
        if column_name not in dataframe.columns:
            st.error(f"Колонка {column_name} отсутствует в данных.")
            return None
        figure_pie_chart = px.pie(
            dataframe,
            names=user_option,
            values=column_name,
        )
        return figure_pie_chart
    else:
        st.error("Count не поддерживается для построения графика.")
        return None


def show_graph():
    if "quantity_selector" in session and session.quantity_selector == "Count":
        total = session.filtered_df.shape[0]
        st.write(f"Общее количество {session.class_selector}: {total}")
    else:
        if session["qset_columns"] is not None:
            st.subheader(
                f"{session.class_selector} - {session.quantity_selector}")
            graph = load_graph(
                session["filtered_df"], session["qset_selector"], session["quantity_selector"], session["sort_options"]
            )
            if graph is not None:
                st.plotly_chart(graph)


def analyze_ifc_attributes(selected_class):
    def get_attributes(entity):
        return {attribute: getattr(entity, attribute) for attribute in dir(entity) if not attribute.startswith('_') and not callable(getattr(entity, attribute))}

    ifc_model = session.get("ifc_file")
    elements = ifc_model.by_type(selected_class)

    attribute_stats = {}
    for element in elements:
        attributes = get_attributes(element)
        for attr_name, attr_value in attributes.items():
            if attr_name not in attribute_stats:
                attribute_stats[attr_name] = {'filled': 0, 'empty': 0}
            if attr_value:
                attribute_stats[attr_name]['filled'] += 1
            else:
                attribute_stats[attr_name]['empty'] += 1

    attribute_stats = {k: v for k,
                       v in attribute_stats.items() if v['filled'] > 0}

    attr_names = list(attribute_stats.keys())
    filled_counts = [attribute_stats[attr]['filled'] for attr in attr_names]
    empty_counts = [attribute_stats[attr]['empty'] for attr in attr_names]

    x = range(len(attr_names))

    colors = ['g' if empty_counts[i] ==
              0 else 'b' for i in range(len(attr_names))]

    plt.figure(figsize=(15, 10))
    for i in range(len(attr_names)):
        if empty_counts[i] == 0:
            plt.bar(i, filled_counts[i], width=0.4, color='g', align='center')
        else:
            plt.bar(i, filled_counts[i], width=0.4, color='b', align='center')
            plt.bar(i, empty_counts[i], width=0.4, color='r', align='edge')

    # Добавляем легенду один раз
    plt.bar(0, 0, color='g', label='Полностью заполнен')
    plt.bar(0, 0, color='b', label='Заполнен')
    plt.bar(0, 0, color='r', label='Пустой')

    plt.xlabel('Атрибуты', fontsize=14)
    plt.ylabel('Количество', fontsize=14)
    plt.title(
        f'Статус заполнения атрибутов для {selected_class} в модели IFC', fontsize=16)
    plt.xticks(x, attr_names, rotation=90, fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(fontsize=12)
    plt.tight_layout()
    st.pyplot(plt)
