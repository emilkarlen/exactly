from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.test_case.help.instruction_description import Description, InvokationVariant


class TheDescriptionBase(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return "Executes the given program using the system's shell."

    def main_description_rest(self) -> list:
        raise NotImplementedError()

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'PROGRAM ARGUMENT...',
                    single_para('A plain file.')),
        ]
