from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency


class StringWithDirDependency(MultiDirDependentValue):
    pass


class StringFragment(StringWithDirDependency):
    """
    A fragment that, together with other fragments, makes up a `StringValue`
    """
    pass


class StringValue(StringWithDirDependency):
    def __init__(self, fragments: tuple):
        self._fragments = fragments

    @property
    def fragments(self) -> tuple:
        return self._fragments

    def resolving_dependencies(self) -> set:
        ret_val = set()
        for fragment in self._fragments:
            ret_val.update(fragment.resolving_dependencies())
        return ret_val

    def has_dir_dependency(self) -> bool:
        return bool(self.resolving_dependencies())

    def exists_pre_sds(self) -> bool:
        return ResolvingDependency.NON_HOME not in self.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> str:
        fragment_strings = [f.value_when_no_dir_dependencies()
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> str:
        fragment_strings = [f.value_of_any_dependency(home_and_sds)
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def __str__(self):
        return '{}([{}])'.format('StringValue',
                                 ','.join(map(str, self._fragments)))
