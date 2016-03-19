class TestSuiteSectionHelp(tuple):
    def __new__(cls,
                name: str):
        return tuple.__new__(cls, (name,))

    @property
    def name(self) -> str:
        return self[0]


class TestSuiteHelp(tuple):
    def __new__(cls,
                test_suite_section_helps: iter):
        return tuple.__new__(cls, (list(test_suite_section_helps),))

    @property
    def section_helps(self) -> list:
        return self[0]
