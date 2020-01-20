from abc import ABC, abstractmethod
from typing import List, Optional

from exactly_lib.definitions import path as path_texts
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib_test.test_resources import arguments_building
from exactly_lib_test.test_resources.arguments_building import SequenceOfElementsBase, ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


def rel_symbol_arg(symbol_name: str) -> ArgumentElementsRenderer:
    return arguments_building.SequenceOfElements([
        arguments_building.OptionArgument(path_texts.REL_SYMBOL_OPTION_NAME),
        symbol_name,
    ])


class PathArgument(SequenceOfElementsBase, ABC):
    """
    Renders a path argument with optional relativity option.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class _PathArgumentWithRelativityOptionFromRenderer(PathArgument):
    """
    Renders a path argument with optional relativity option.
    """

    def __init__(self,
                 name: str,
                 relativity: Optional[ArgumentElementsRenderer] = None):
        self._name = name
        self.relativity_argument = relativity

    @property
    def name(self) -> str:
        return self._name

    @property
    def elements(self) -> List[WithToString]:
        if self.relativity_argument is None:
            return [self.name]
        else:
            return [self.relativity_argument,
                    self.name]


def path_argument(name: str,
                  relativity: Optional[ArgumentElementsRenderer] = None) -> PathArgument:
    return _PathArgumentWithRelativityOptionFromRenderer(name, relativity)


def symbol_path_argument(symbol_name: str) -> PathArgument:
    return path_argument(symbol_reference_syntax_for_name(symbol_name))


class RelOptPathArgument(PathArgument):
    """
    Renders a path argument with optional relativity option.
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
    def elements(self) -> List[WithToString]:
        if self._relativity_option is None:
            return [self.name]
        else:
            return [rel_option_type_arg(self._relativity_option),
                    self.name]


def rel_option_type_arg(relativity: RelOptionType) -> ArgumentElementsRenderer:
    return arguments_building.OptionArgument(REL_OPTIONS_MAP[relativity].option_name)
