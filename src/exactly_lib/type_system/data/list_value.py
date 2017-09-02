from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system import utils


class ListValue(MultiDirDependentValue):
    def __init__(self, string_value_elements: list):
        """
        :param string_value_elements: list of :class:`StringValue`
        """
        self._string_value_elements = tuple(string_value_elements)

    @property
    def string_value_elements(self) -> tuple:
        return self._string_value_elements

    def resolving_dependencies(self) -> set:
        return utils.resolving_dependencies_from_sequence(self._string_value_elements)

    def value_when_no_dir_dependencies(self) -> list:
        """
        :rtype: List of `str`
        """
        return [e.value_when_no_dir_dependencies()
                for e in self._string_value_elements]

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> list:
        """
        :rtype: List of `str`
        """
        return [e.value_of_any_dependency(home_and_sds)
                for e in self._string_value_elements]

    def __str__(self):
        return '{}([{}])'.format('ListValue',
                                 ','.join(map(str, self._string_value_elements)))
