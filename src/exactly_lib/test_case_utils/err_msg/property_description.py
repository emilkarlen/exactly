from typing import Sequence

from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor, NoErrorMessagePartConstructor, \
    ErrorMessagePartFixConstructor, MultipleErrorMessagePartFixConstructor
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescription, \
    PropertyDescriptor

OBJECT_DESCRIPTOR_PARTS_SEPARATOR_LINES = ['']


def multiple_object_descriptors__fixed(
        part_constructors: Sequence[ErrorMessagePartFixConstructor]) -> ErrorMessagePartFixConstructor:
    return MultipleErrorMessagePartFixConstructor(OBJECT_DESCRIPTOR_PARTS_SEPARATOR_LINES, part_constructors)


class PropertyDescriptorWithConstantPropertyName(PropertyDescriptor):
    def __init__(self,
                 name: str,
                 object_descriptor: ErrorMessagePartConstructor):
        self._name = name
        self._object_descriptor = object_descriptor

    def description(self) -> PropertyDescription:
        return PropertyDescription(self._name,
                                   self._object_descriptor.lines())


class PropertyDescriptorWithConstantPropertyNameOfFix(PropertyDescriptor):
    def __init__(self,
                 name: str,
                 object_descriptor: ErrorMessagePartFixConstructor):
        self._name = name
        self._object_descriptor = object_descriptor

    def description(self) -> PropertyDescription:
        return PropertyDescription(self._name,
                                   self._object_descriptor.lines())


def property_descriptor_with_just_a_constant_name(name: str) -> PropertyDescriptor:
    return PropertyDescriptorWithConstantPropertyName(
        name,
        NoErrorMessagePartConstructor(),
    )


def file_property_name(contents_attribute: str, object_name: str) -> str:
    return contents_attribute + ' of ' + object_name
