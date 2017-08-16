from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


class LinesConstructor:
    """Constructs lines that are part of an error message."""

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        """
        :return: empty list if there is nothing to say
        """
        raise NotImplementedError('abstract method')


class NoLinesConstructor(LinesConstructor):
    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        return []


class PropertyDescription:
    def __init__(self,
                 name: str,
                 details_lines: list):
        self._name = name
        self._details_lines = details_lines

    @property
    def name(self) -> str:
        return self._name

    @property
    def details_lines(self) -> list:
        return self._details_lines


class PropertyDescriptor:
    def description(self, environment: InstructionEnvironmentForPostSdsStep
                    ) -> PropertyDescription:
        raise NotImplementedError('abstract method')


class PropertyDescriptorWithConstantPropertyName(PropertyDescriptor):
    def __init__(self,
                 name: str,
                 details_descriptor: LinesConstructor):
        self._name = name
        self._details_descriptor = details_descriptor

    def description(self, environment: InstructionEnvironmentForPostSdsStep
                    ) -> PropertyDescription:
        return PropertyDescription(self._name,
                                   self._details_descriptor.lines(environment))


def property_descriptor_with_just_a_constant_name(name: str) -> PropertyDescriptor:
    return PropertyDescriptorWithConstantPropertyName(
        name,
        NoLinesConstructor(),
    )
