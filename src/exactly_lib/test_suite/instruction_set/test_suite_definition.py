from exactly_lib.section_document import document_parser


class TestSuiteDefinition(tuple):
    def __new__(cls,
                configuration_section_instructions: dict,
                configuration_section_parser: document_parser.SectionElementParser):
        """
        :param configuration_section_instructions: instruction-name -> `SingleInstructionSetup`.
        """
        return tuple.__new__(cls, (configuration_section_instructions,
                                   configuration_section_parser))

    @property
    def configuration_section_instructions(self) -> dict:
        """
        :rtype instruction-name -> `SingleInstructionSetup`
        """
        return self[0]

    @property
    def configuration_section_parser(self) -> document_parser.SectionElementParser:
        return self[1]
