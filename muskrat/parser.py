#!/usr/bin/python3

class Parser:
    def __init__(self):
        self.objects = []

    def get(self, behind=1, condition=lambda x: True):
        for obj in reversed(self.objects):
            fc, behind = obj.dive(behind, condition)
            if fc is not None:
                return fc
        return None

    def append(self, obj):
        self.objects.append(obj)


class ParsingObject:
    def __init__(self, content, object_type, using_methods):
        self.connected_objects = []
        self.using_methods = using_methods
        self.content = content
        self.properties = ObjectProperties()
        self.object_type = object_type

    def connect(self, object2connect):
        self.connected_objects.append(object2connect)

    def dive(self, counter=1, condition=lambda x: True):
        for obj in reversed(self.connected_objects):
            if condition(obj):
                counter -= 1
            if counter < 0:
                break
            elif not counter:
                return self, 0
            found_child, counter = obj.dive(counter, condition)
            if found_child is not None:
                return found_child, counter
        return None, counter

    def insert_content(self, content2insert, update_function=None):
        self.content += content2insert
        if update_function is not None:
            self.content = update_function(self.content)


class ObjectProperties:
    def __init__(self):
        self.both_side = {}
        self.bool_like = {}

    def add_property(self, key, value=None):
        if value is None:
            self.bool_like[key] = None
        else:
            self.both_side[key] = value

    def get_property(self, key):
        if key in self.both_side:
            return self.both_side[key]
        elif key in self.bool_like:
            return self.bool_like[key]

    def set_property(self, key, value):
        if key in self.both_side:
            self.both_side[key] = value
        else:
            raise ValueError

    def remove_property(self, key):
        if key in self.both_side:
            del self.both_side[key]
        elif key in self.bool_like:
            del self.bool_like[key]


class UsingMethods:
    def __init__(self):
        self.__methods = {}

    def connect_method(self, object_types):
        self.__methods['connect'] = object_types

    def append_method(self):
        self.__methods['append'] = True

    def insert_back_method(self):
        self.__methods['insert_back'] = True

    def insert_forward_method(self):
        self.__methods['insert_forward'] = True

    def able_to(self, method, obj):
        if method not in self.__methods:
            return False
        elif type(self.__methods[method]) == bool:
            return True
        elif obj.object_type in self.__methods[method]:
            return True
        else:
            return False


class ObjectGrouping:
    def __init__(self, object_type=None):
        self.object_type = object_type
        self.groups = []

    def set_object_type(self, object_type):
        if object_type is not None:
            raise ValueError()
        self.object_type = object_type

    def add_group(self, group_key, update_function=None):
        if update_function:
            group_key = update_function(group_key)
        self.groups.append(ObjectGroup(group_key))

    def append_to_last_group(self, obj):
        self.groups[-1].append_object(obj)

    def get_last(self):
        if self.groups:
            return self.groups[-1].get_last()

    def get_last_by_type(self, object_type):
        if object_type == self.object_type:
            return self.get_last()

    def connect(self, object2connect):
        self.get_last().connect(object2connect)

    def insert_content(self, content2insert, update_function=None):
        self.get_last().insert_content(content2insert, update_function)


class ObjectGroup:
    def __init__(self, group_key):
        self.group_key = group_key
        self.subobjects = []

    def get_last(self):
        return self.subobjects[-1]

    def append_object(self, obj2append):
        self.subobjects.append(obj2append)


class LineProcessing:
    def __init__(self, line_text):
        self.line_units = line_text.split()
        self.current_index = 0

    def current(self):
        return self.line_units[self.current_index]

    def next(self, add=0):
        return self.line_units[self.current_index + 1 + add]


class ParsingUnit:
    def __init__(self, line_units, unit_index):
        self.content = line_units[unit_index]

    def what(self):
        ...


class UnitEntity:
    def __init__(self):