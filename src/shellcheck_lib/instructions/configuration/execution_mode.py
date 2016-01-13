from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.general.textformat.parse import normalize_and_parse
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.paragraph import *
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, ConfigurationBuilder, ExecutionMode
from shellcheck_lib.test_case.sections.result import sh

NAME_NORMAL = 'NORMAL'
NAME_SKIP = 'SKIP'
NAME_XFAIL = 'XFAIL'

NAME_2_MODE = {
    NAME_NORMAL: ExecutionMode.NORMAL,
    NAME_SKIP: ExecutionMode.SKIPPED,
    NAME_XFAIL: ExecutionMode.XFAIL,
}


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Sets execution mode.'

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'MODE',
                    [
                        lists.HeaderContentList([
                            lists.HeaderContentListItem(Text(NAME_NORMAL),
                                                        normalize_and_parse("""\
                                                        The test case is executed and expected to pass.


                                                        This is the default mode.""")
                                                        ),
                            lists.HeaderContentListItem(Text(NAME_SKIP),
                                                        normalize_and_parse("""\
                                                        The test case is not executed.


                                                        Result of the test case is %s."""
                                                                            % FullResultStatus.SKIPPED.name)
                                                        ),
                            lists.HeaderContentListItem(Text(NAME_XFAIL),
                                                        normalize_and_parse("""\
                                                        The test case is expected to fail.


                                                        Result of the test case is {on_fail}, if the test case fails.

                                                        If it passes, the result is {on_pass}.""".format(
                                                                on_fail=FullResultStatus.XFAIL.name,
                                                                on_pass=FullResultStatus.XPASS.name)
                                                        )),
                        ],
                                lists.Format(lists.ListType.VARIABLE_LIST))
                    ])
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AnonymousPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if len(arguments) != 1:
            msg = 'Invalid number of arguments (exactly one expected), found {}'.format(str(len(arguments)))
            raise SingleInstructionInvalidArgumentException(msg)
        argument = arguments[0].upper()
        try:
            target = NAME_2_MODE[argument]
        except KeyError:
            raise SingleInstructionInvalidArgumentException('Invalid mode: `%s`' % arguments[0])
        return _Instruction(target)


class _Instruction(AnonymousPhaseInstruction):
    def __init__(self,
                 mode_to_set: ExecutionMode):
        self.mode_to_set = mode_to_set

    def main(self,
             global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.mode_to_set)
        return sh.new_sh_success()
