class CommandLine:
    def __init__(self,
                 program_name: str,
                 argument_usages: list):
        self._program_name = program_name
        self._argument_usages = argument_usages

    @property
    def program_name(self) -> str:
        return self._program_name

    @property
    def argument_usages(self) -> list:
        """
        :rtype: [`ArgumentUsage`]
        """
        return self._argument_usages
