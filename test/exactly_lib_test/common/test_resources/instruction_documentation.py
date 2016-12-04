from exactly_lib.common.instruction_documentation import InstructionDocumentation, SyntaxElementDescription, \
    InvokationVariant
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib_test.test_resources.instruction_description import InstructionDocumentationWithConstantValues

SYNTAX_ELEMENT_DESCRIPTIONS = [
    SyntaxElementDescription('syntax element name',
                             docs.paras('syntax element description rest'))]

INVOKATION_VARIANTS = [InvokationVariant('invokation variant syntax')]


def instruction_documentation(instruction_name: str) -> InstructionDocumentation:
    return InstructionDocumentationWithConstantValues(instruction_name,
                                                      'single line description',
                                                      'main description rest',
                                                      INVOKATION_VARIANTS,
                                                      SYNTAX_ELEMENT_DESCRIPTIONS)
