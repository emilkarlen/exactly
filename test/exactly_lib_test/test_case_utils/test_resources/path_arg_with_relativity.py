from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


class PathArgumentWithRelativity:
    def __init__(self,
                 file_name: str,
                 relativity: RelativityOptionConfiguration
                 ):
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
        return self.relativity.option_string + ' ' + self.file_name
