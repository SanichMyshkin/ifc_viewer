import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

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


def plot_element_distribution(dataframe):
    st.subheader('Распределение элементов по классам')
    class_counts = dataframe['Class'].value_counts()
    fig, ax = plt.subplots()
    colors = plt.cm.viridis(np.linspace(0, 1, len(class_counts)))
    ax.bar(class_counts.index, class_counts.values, color=colors)
    ax.set_ylabel('Количество')
    plt.xticks(rotation=45, ha='right')
    for i, count in enumerate(class_counts):
        ax.text(
            i, count, f'{count / class_counts.sum() * 100:.1f}%', ha='center', va='bottom')
    plt.tight_layout()
    st.pyplot(fig)
