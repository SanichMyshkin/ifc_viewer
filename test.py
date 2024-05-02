import ifcopenshell

# Открываем файл IFC
file_path = "/Users/sanichmyskin/Desktop/Proga/ifc_viewer/templates/ArchiCad.ifc"
ifc_file = ifcopenshell.open(file_path)

# Получаем все объекты из файла
objects = ifc_file.by_type("IfcWall")  # здесь можно указать тип нужного объекта

# Проходимся по каждому объекту и выводим его свойства
for obj in objects:
    print("Имя объекта:", obj.Name if hasattr(obj, "Name") else "Нет имени")
    print("Тип объекта:", obj.is_a())
    # Пример получения высоты объекта
    if hasattr(obj, "OverallHeight"):
        print("Высота:", obj.OverallHeight)
    else:
        print("Высота не указана")
    # Пример получения материала стены
    if hasattr(obj, "Material"):
        print("Материал:", obj.Material.Name if hasattr(obj.Material, "Name") else "Нет информации о материале")
    else:
        print("Материал не указан")
    # Другие свойства и характеристики объекта можно получить аналогичным образом
    print("-" * 50)
