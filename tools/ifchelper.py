import ifcopenshell.util.element as Element


def get_objects_data_by_class(file, class_type):
    def add_pset_attributes(psets):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(
                    f"{pset_name}.{property_name}"
                ) if property_name != "id" else None

    objects = file.by_type(class_type)
    objects_data = []
    pset_attributes = set()

    for object in objects:
        qtos = Element.get_psets(object, qtos_only=True)
        add_pset_attributes(qtos)
        psets = Element.get_psets(object, psets_only=True)
        add_pset_attributes(psets)
        objects_data.append(
            {
                "ExpressId": object.id(),
                "GlobalId": object.GlobalId,
                "Class": object.is_a(),
                "PredefinedType": Element.get_predefined_type(object),
                "Name": object.Name,
                "Level": Element.get_container(object).Name
                if Element.get_container(object)
                else "",
                "Type": Element.get_type(object).Name
                if Element.get_type(object)
                else "",
                "QuantitySets": qtos,
                "PropertySets": psets,
            }
        )
    return objects_data, list(pset_attributes)


def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".", 1)[0]
        prop_name = attribute.split(".", -1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        elif pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
        else:
            return None


def create_pandas_dataframe(data, pset_attributes):
    import pandas as pd

    # Лист Атрибутов
    attributes = [
        "ExpressId",
        "GlobalId",
        "Class",
        "PredefinedType",
        "Name",
        "Level",
        "Type",
    ] + pset_attributes
    # Эксопрт данных в Pandas
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))
    return pd.DataFrame.from_records(pandas_data, columns=attributes)


def format_ifcjs_psets(ifcJSON):
    """
    Organise pset data from web-ifc-api response
    """
    dict = {}
    for pset in ifcJSON:
        if "Qto" in pset["Name"]["value"]:
            for quantity in pset["Quantities"]:
                quantity_name = quantity["Name"]["value"]
                quantity_value = ""
                for key in quantity.keys():
                    if "Value" in key:
                        quantity_value = quantity[key]["value"]
                # quantity_value = quantity[5]["value"]
                if pset["expressID"] not in dict:
                    dict[pset["expressID"]] = {
                        "Name": pset["Name"]["value"],
                        "Data": []
                    }
                dict[pset["expressID"]]["Data"].append({
                    "Name": quantity_name,
                    "Value": quantity_value
                })
        if "Pset" in pset["Name"]["value"]:
            for property in pset["HasProperties"]:
                property_name = property["Name"]["value"]
                property_value = ""
                for key in property.keys():
                    if "Value" in key:
                        property_value = property[key]["value"]
                if pset["expressID"] not in dict:
                    dict[pset["expressID"]] = {
                        "Name": pset["Name"]["value"],
                        "Data": []
                    }
                dict[pset["expressID"]]["Data"].append({
                    "Name": property_name,
                    "Value": property_value
                })
    return dict
