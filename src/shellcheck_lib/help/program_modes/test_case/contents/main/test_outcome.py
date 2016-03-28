from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib.cli.cli_environment.exit_values import ALL_EXIT_VALUES, ExitValue
from shellcheck_lib.execution.result import PartialResultStatus, FullResultStatus
from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.instructions.configuration import execution_mode
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure.structures import *


def test_outcome_documentation(setup: Setup) -> doc.SectionContents:
    preamble_paragraphs = normalize_and_parse(PREAMBLE)
    return doc.SectionContents(
        preamble_paragraphs,
        [
            section('Reporting',
                    normalize_and_parse(REPORTING)),
            section('Fully executed test case',
                    _description_of_full_execution(setup)),
            section('Interrupted execution',
                    _interrupted_execution(setup)),
            section('Invalid command line',
                    [para('TODO: Alltid exit-kod 2 - måste kolla varifrån den härleds. '
                          'Dock 3 om fil saknas - då detta kollas inte av ArgumentParser')]),
            section('Exit codes and identifiers',
                    [_all_exit_values(setup)]),
        ]
    )


PREAMBLE = ''

REPORTING = """\
TODO: Lite knepigt att dra in även fallet med felaktig kommandorad här, men
vet inte hur man kan komma runt det.

Ev kan det nämnas under rubriken 'Invalid command line', men då blir
just det här avsnittet aningen missvisande.


If command line arguments are valid, then
the outcome is reported by an exitcode and an identifier printed as a single line on stdout.

Otherwise, only an exitcode is used.
"""


def _description_of_full_execution(setup: Setup) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(FULL_EXECUTION_PREAMBLE))
    ret_val.append(_what_outcome_depends_on(setup))
    ret_val.append(_outcomes_per_mode_and_assert(setup))
    return ret_val


FULL_EXECUTION_PREAMBLE = """The outcome of a fully executed test case depends on two things:"""


def _what_outcome_depends_on(setup: Setup) -> ParagraphItem:
    items = [
        list_item("""The "execution mode" set by the {phase[configuration]} phase""".format(phase=setup.phase_names),
                  [para('The default mode is {default_mode}.'.format(default_mode=execution_mode.NAME_NORMAL))]),
        list_item("""The outcome of the {phase[assert]} phase""".format(phase=setup.phase_names),
                  []),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ORDERED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


def _outcomes_per_mode_and_assert(setup: Setup) -> ParagraphItem:
    def _row(mode: str, assert_outcome: PartialResultStatus, test_outcome: FullResultStatus) -> list:
        return [paras(mode),
                paras(assert_outcome.name if assert_outcome is not None else ''),
                paras(test_outcome.name)
                ]

    return first_row_is_header_table([
        [
            paras('Mode'),
            paras('{phase[assert]:syntax}'.format(phase=setup.phase_names)),
            paras('Test Case')],
        _row(execution_mode.NAME_NORMAL, PartialResultStatus.PASS, FullResultStatus.PASS),
        _row(execution_mode.NAME_NORMAL, PartialResultStatus.FAIL, FullResultStatus.FAIL),

        _row(execution_mode.NAME_XFAIL, PartialResultStatus.PASS, FullResultStatus.XPASS),
        _row(execution_mode.NAME_XFAIL, PartialResultStatus.FAIL, FullResultStatus.XFAIL),

        _row(execution_mode.NAME_SKIP, None, FullResultStatus.SKIPPED),
    ],
        '  ')


def _interrupted_execution(setup: Setup) -> list:
    values = [
        exit_values.EXECUTION__VALIDATE,
        exit_values.EXECUTION__HARD_ERROR,
        exit_values.EXECUTION__IMPLEMENTATION_ERROR,
    ]
    return [
        para('TODO: lista o förklara varje värde för sig, på nått sätt.'),
        simple_header_only_list([exit_value.exit_identifier for exit_value in values],
                                lists.ListType.ITEMIZED_LIST)
    ]


def _all_exit_values(setup: Setup) -> ParagraphItem:
    def _row(exit_value: ExitValue) -> list:
        return [paras(exit_value.exit_identifier),
                paras(exit_value.exit_identifier),
                paras(str(exit_value.exit_code)),
                ]

    return first_row_is_header_table([
                                         [
                                             paras('Test outcome'),
                                             paras('Exit identifier'),
                                             paras('Exit code')
                                         ]] +
                                     [_row(exit_value) for exit_value in ALL_EXIT_VALUES],
                                     '  ')
