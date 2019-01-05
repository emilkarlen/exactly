from typing import Sequence

from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor, NoErrorMessagePartConstructor, \
    MultipleErrorMessagePartConstructor
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescription, \
    PropertyDescriptor

OBJECT_DESCRIPTOR_PARTS_SEPARATOR_LINES = ['']


def multiple_object_descriptors(
        part_constructors: Sequence[ErrorMessagePartConstructor]) -> ErrorMessagePartConstructor:
    return MultipleErrorMessagePartConstructor(OBJECT_DESCRIPTOR_PARTS_SEPARATOR_LINES, part_constructors)


class PropertyDescriptorWithConstantPropertyName(PropertyDescriptor):
    def __init__(self,
                 name: str,
                 object_descriptor: ErrorMessagePartConstructor):
        self._name = name
        self._object_descriptor = object_descriptor

    def description(self, environment: ErrorMessageResolvingEnvironment
                    ) -> PropertyDescription:
        return PropertyDescription(self._name,
                                   self._object_descriptor.lines(environment))


def property_descriptor_with_just_a_constant_name(name: str) -> PropertyDescriptor:
    return PropertyDescriptorWithConstantPropertyName(
        name,
        NoErrorMessagePartConstructor(),
    )


def file_property_name(contents_attribute: str, object_name: str) -> str:
    return contents_attribute + ' of ' + object_name
