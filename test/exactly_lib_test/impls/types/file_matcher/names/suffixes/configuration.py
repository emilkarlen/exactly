from exactly_lib.definitions.primitives import file_matcher
from exactly_lib_test.impls.types.file_matcher.names.test_resources import configuration, name_parts
from exactly_lib_test.impls.types.file_matcher.names.test_resources.configuration import Configuration
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import NameVariant
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer


class _Configuration(name_parts.NamePartsConfiguration):
    @property
    def node_name(self) -> str:
        return file_matcher.SUFFIXES_MATCHER_NAME

    def arguments(self, condition: NameVariant) -> ArgumentElementsRenderer:
        return argument_building.Suffixes(condition)

    def file_name_ending_with(self, s: str) -> str:
        return '.' + s

    def get_name_part(self, case: name_parts.Case) -> str:
        return case.suffixes


class TestCaseBaseForSuffixes(configuration.TestCaseBase):
    _CONF = _Configuration()

    @property
    def conf(self) -> Configuration:
        return self._CONF
