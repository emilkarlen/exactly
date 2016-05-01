class TestSuiteHelp(tuple):
    def __new__(cls,
                test_suite_section_helps: iter):
        """
        :type test_suite_section_helps: [`SectionDocumentation`]
        """
        return tuple.__new__(cls, (list(test_suite_section_helps),))

    @property
    def section_helps(self) -> list:
        """
        :rtype: [`SectionDocumentation`]
        """
        return self[0]
