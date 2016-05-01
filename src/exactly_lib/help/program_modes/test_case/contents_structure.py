class TestCaseHelp(tuple):
    def __new__(cls,
                phase_helps: iter):
        """
        :type phase_helps: [`SectionDocumentation`]
        """
        return tuple.__new__(cls, (list(phase_helps),))

    @property
    def phase_helps_in_order_of_execution(self) -> list:
        """
        :type: [`SectionDocumentation`]
        """
        return self[0]

    @property
    def phase_name_2_phase_help(self) -> dict:
        """
        :type: `str` -> `SectionDocumentation`
        """
        return dict(map(lambda ph_help: (ph_help.name.plain, ph_help),
                        self.phase_helps_in_order_of_execution))
