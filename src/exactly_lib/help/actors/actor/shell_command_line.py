from exactly_lib.help.actors.names_and_cross_references import SHELL_COMMAND_LINE_ACTOR
from exactly_lib.help.actors.single_command_line_base import SingleCommandLineActorDocumentationBase
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.textformat.structure.document import SectionContents


class ShellCommandLineActorDocumentation(SingleCommandLineActorDocumentationBase):
    def __init__(self):
        super().__init__(SHELL_COMMAND_LINE_ACTOR)
        from exactly_lib.execution.exit_values import EXECUTION__VALIDATE
        format_map = {
            'phase': phase_name_dictionary(),
            'home_directory': HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular,
            'sandbox': SANDBOX_CONCEPT.name().singular,
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'VALIDATION': EXECUTION__VALIDATE.exit_identifier,
        }
        self._parser = TextParser(format_map)

    def single_line_description_str(self) -> str:
        return self._parser.format('Executes a shell command')

    def act_phase_contents(self) -> SectionContents:
        return SectionContents(self._parser.fnap(_ACT_PHASE_CONTENTS))


DOCUMENTATION = ShellCommandLineActorDocumentation()

_ACT_PHASE_CONTENTS = """\
The command line uses shell syntax for quoting and separation of program file name and arguments.


The first element must be the path of an existing, executable file.


If the path is relative, then it is taken to be relative the {home_directory}.


If the path is not an existing executable file, then this will cause a {VALIDATION} error,
and the test case will not be executed.
"""
