from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx


class PathArgumentWithRelativity:
    def __init__(self,
                 file_name: str,
                 relativity: RelativityOptionConfiguration):
        self._file_name = file_name
        self._relativity = relativity

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def relativity(self) -> RelativityOptionConfiguration:
        return self._relativity

    @property
    def argument_str(self) -> str:
        return self.relativity.option_argument_str + ' ' + self.file_name

    @property
    def argument_abs_stx(self) -> PathAbsStx:
        return self._relativity.path_abs_stx_of_name(self._file_name)

    @property
    def as_argument_element(self) -> ArgumentElementsRenderer:
        return self.relativity.path_argument_of_rel_name(self.file_name)
