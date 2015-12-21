from shellcheck_lib.document import model
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource


class InvokationVariant:
    def __init__(self,
                 syntax: str,
                 description_rest: str):
        self.syntax = syntax
        self.description_rest = description_rest


class SyntaxElementDescription:
    def __init__(self,
                 element_name: str,
                 description_rest: str,
                 invokation_variants: list):
        self.element_name = element_name
        self.invokation_variants = invokation_variants
        self.description_rest = description_rest


class Description:
    def __init__(self,
                 single_line_description: str,
                 main_description_rest: str,
                 invokation_variants: list,
                 syntax_element_descriptions: iter = ()):
        """
        :param invokation_variants: [InvokationVariant]
        :param syntax_element_descriptions: [SyntaxElementDescription]
        """
        self.__single_line_description = single_line_description
        self.__main_description_rest = main_description_rest
        self.__invokation_variants = invokation_variants
        self.__syntax_element_descriptions = syntax_element_descriptions

    @property
    def single_line_description(self) -> str:
        return self.__single_line_description

    @property
    def main_description_rest(self) -> str:
        return self.__main_description_rest

    @property
    def invokation_variants(self) -> list:
        return self.__invokation_variants

    @property
    def syntax_element_descriptions(self) -> iter:
        return self.__syntax_element_descriptions


class SingleInstructionSetup(SingleInstructionParser):
    def __init__(self,
                 parser: SingleInstructionParser,
                 description: Description):
        self._parser = parser
        self._description = description

    @property
    def description(self) -> Description:
        return self._description

    def apply(self, source: SingleInstructionParserSource) -> model.Instruction:
        return self._parser.apply(source)


class InstructionsSetup:
    def __init__(self,
                 config_instruction_set: dict,
                 setup_instruction_set: dict,
                 assert_instruction_set: dict,
                 cleanup_instruction_set: dict):
        """
        Each dictionary is a mapping: instruction-name -> SingleInstructionSetup.

        Each SingleInstructionSetup should parse and construct an instruction for
         the correct phase (of course). I.e., sub classes of Instruction.
        """
        self._config_instruction_set = config_instruction_set
        self._setup_instruction_set = setup_instruction_set
        self._assert_instruction_set = assert_instruction_set
        self._cleanup_instruction_set = cleanup_instruction_set

    @property
    def config_instruction_set(self) -> dict:
        return self._config_instruction_set

    @property
    def setup_instruction_set(self) -> dict:
        return self._setup_instruction_set

    @property
    def assert_instruction_set(self) -> dict:
        return self._assert_instruction_set

    @property
    def cleanup_instruction_set(self) -> dict:
        return self._cleanup_instruction_set
