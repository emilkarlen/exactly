from exactly_lib.util.description import DescriptionWithSubSections


class CliProgramSyntaxDocumentation:
    def __init__(self, program_name: str):
        self.program_name = program_name

    def description(self) -> DescriptionWithSubSections:
        raise NotImplementedError()

    def initial_paragraphs(self) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return []

    def synopsises(self) -> list:
        """
        :rtype: [`Synopsis`]
        """
        raise NotImplementedError()

    def argument_descriptions(self) -> list:
        """
        :rtype: [`DescribedArgument`]
        """
        return []
