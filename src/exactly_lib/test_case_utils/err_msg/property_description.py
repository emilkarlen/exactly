from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor, NoErrorMessagePartConstructor, \
    MultipleErrorMessagePartConstructor

OBJECT_DESCRIPTOR_PARTS_SEPARATOR_LINES = ['']


def multiple_object_descriptors(part_constructors: list) -> ErrorMessagePartConstructor:
    return MultipleErrorMessagePartConstructor(OBJECT_DESCRIPTOR_PARTS_SEPARATOR_LINES, part_constructors)


class PropertyDescription:
    def __init__(self,
                 name: str,
                 object_description_lines: list):
        self._name = name
        self._details_lines = object_description_lines

    @property
    def name(self) -> str:
        return self._name

    @property
    def object_description_lines(self) -> list:
        return self._details_lines


class PropertyDescriptor:
    def description(self, environment: InstructionEnvironmentForPostSdsStep
                    ) -> PropertyDescription:
        raise NotImplementedError('abstract method')


class PropertyDescriptorWithConstantPropertyName(PropertyDescriptor):
    def __init__(self,
                 name: str,
                 object_descriptor: ErrorMessagePartConstructor):
        self._name = name
        self._object_descriptor = object_descriptor

    def description(self, environment: InstructionEnvironmentForPostSdsStep
                    ) -> PropertyDescription:
        return PropertyDescription(self._name,
                                   self._object_descriptor.lines(environment))


def property_descriptor_with_just_a_constant_name(name: str) -> PropertyDescriptor:
    return PropertyDescriptorWithConstantPropertyName(
        name,
        NoErrorMessagePartConstructor(),
    )
