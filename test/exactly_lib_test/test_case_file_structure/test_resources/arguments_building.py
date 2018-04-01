from typing import Sequence

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib_test.test_resources import arguments_building
from exactly_lib_test.test_resources.arguments_building import SequenceOfArgumentsBase, ArgumentElementRenderer


def rel_option_type_arg(relativity: RelOptionType) -> ArgumentElementRenderer:
    return arguments_building.OptionArgument(REL_OPTIONS_MAP[relativity].option_name)


def rel_symbol_arg(symbol_name: str) -> ArgumentElementRenderer:
    return arguments_building.SequenceOfArguments([
        arguments_building.OptionArgument(file_ref_texts.REL_SYMBOL_OPTION_NAME),
        symbol_name,
    ])


def file_ref_arg(file_name, relativity: ArgumentElementRenderer = None) -> ArgumentElementRenderer:
    if relativity is None:
        return arguments_building.SequenceOfArguments([file_name])
    else:
        return arguments_building.SequenceOfArguments([relativity, file_name])


class FileRefArgument(SequenceOfArgumentsBase):
    """
    Renders a file ref argument with optional relativity option.
    """

    def __init__(self,
                 name: str,
                 relativity: ArgumentElementRenderer = None):
        self._name = name
        self.relativity_argument = relativity

    @property
    def name(self) -> str:
        return self._name

    @property
    def arguments(self) -> Sequence:
        if self.relativity_argument is None:
            return [self.name]
        else:
            return [self.relativity_argument,
                    self.name]


class RelOptFileRefArgument(SequenceOfArgumentsBase):
    """
    Renders a file ref argument with optional relativity option.
    """

    def __init__(self,
                 name: str,
                 relativity_option: RelOptionType):
        self._name = name
        self._relativity_option = relativity_option

    @property
    def name(self) -> str:
        return self._name

    @property
    def relativity_option(self) -> RelOptionType:
        return self._relativity_option

    @property
    def arguments(self) -> Sequence:
        if self._relativity_option is None:
            return [self.name]
        else:
            return [rel_option_type_arg(self._relativity_option),
                    self.name]
