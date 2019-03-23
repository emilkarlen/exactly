from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.definitions import file_ref as file_ref_texts
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib_test.test_resources import arguments_building
from exactly_lib_test.test_resources.arguments_building import SequenceOfArgumentsBase, ArgumentElementRenderer, \
    Stringable


def rel_symbol_arg(symbol_name: str) -> ArgumentElementRenderer:
    return arguments_building.SequenceOfArguments([
        arguments_building.OptionArgument(file_ref_texts.REL_SYMBOL_OPTION_NAME),
        symbol_name,
    ])


class FileRefArgument(SequenceOfArgumentsBase, ABC):
    """
    Renders a file ref argument with optional relativity option.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def arguments(self) -> Sequence[Stringable]:
        pass


class _FileRefArgumentWithRelativityOptionFromRenderer(FileRefArgument):
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
    def arguments(self) -> Sequence[Stringable]:
        if self.relativity_argument is None:
            return [self.name]
        else:
            return [self.relativity_argument,
                    self.name]


def file_ref_argument(name: str,
                      relativity: ArgumentElementRenderer = None) -> FileRefArgument:
    return _FileRefArgumentWithRelativityOptionFromRenderer(name, relativity)


def symbol_file_ref_argument(symbol_name: str) -> FileRefArgument:
    return file_ref_argument(symbol_reference_syntax_for_name(symbol_name))


class RelOptFileRefArgument(FileRefArgument):
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
    def arguments(self) -> Sequence[Stringable]:
        if self._relativity_option is None:
            return [self.name]
        else:
            return [rel_option_type_arg(self._relativity_option),
                    self.name]


def rel_option_type_arg(relativity: RelOptionType) -> ArgumentElementRenderer:
    return arguments_building.OptionArgument(REL_OPTIONS_MAP[relativity].option_name)
