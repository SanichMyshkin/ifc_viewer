import ifcopenshell.util.element as Element
import pandas as pd
import streamlit as st

cache = st.session_state


def fetch_elements_by_class(ifc_file, class_type):
    def collect_pset_attributes(psets, attribute_set):
        for pset_name, properties in psets.items():
            for property_name in properties.keys():
                if property_name != "id":
                    attribute_set.add(f"{pset_name}.{property_name}")

    elements = ifc_file.by_type(class_type)
    element_data_list = []
    pset_attributes = set()

    for element in elements:
        quantity_sets = Element.get_psets(element, qtos_only=True)
        collect_pset_attributes(quantity_sets, pset_attributes)
        property_sets = Element.get_psets(element, psets_only=True)
        collect_pset_attributes(property_sets, pset_attributes)
        element_data_list.append(
            {
                "ExpressId": element.id(),
                "GlobalId": element.GlobalId,
                "Class": element.is_a(),
                "PredefinedType": Element.get_predefined_type(element),
                "Name": element.Name,
                "Level": Element.get_container(element).Name if Element.get_container(element) else "",
                "Type": Element.get_type(element).Name if Element.get_type(element) else "",
                "QuantitySets": quantity_sets,
                "PropertySets": property_sets,
            }
        )
    return element_data_list, list(pset_attributes)


def fetch_attribute_value(element_data, attribute):
    if "." not in attribute:
        return element_data.get(attribute)
    pset_name, property_name = attribute.split(".", 1)
    pset_data = element_data.get("PropertySets", {}).get(
        pset_name) or element_data.get("QuantitySets", {}).get(pset_name)
    return pset_data.get(property_name) if pset_data else None


def create_dataframe(element_data_list, pset_attributes):
    attributes = [
        "ExpressId",
        "GlobalId",
        "Class",
        "PredefinedType",
        "Name",
        "Level",
        "Type",
    ] + pset_attributes

    rows = []
    for element_data in element_data_list:
        row = [fetch_attribute_value(element_data, attr)
               for attr in attributes]
        rows.append(tuple(row))

    return pd.DataFrame.from_records(rows, columns=attributes)


def fetch_ifc_element_data(ifc_element_id):
    element_id = ifc_element_id['id']
    if element_id:
        ifc_file = cache.ifc_file
        element = ifc_file.by_id(element_id)
        quantity_sets = Element.get_psets(element, qtos_only=True)
        property_sets = Element.get_psets(element, psets_only=True)
        element_name = element[2]
        return element_name, quantity_sets, property_sets
