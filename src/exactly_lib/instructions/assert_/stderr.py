from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents import stdout_stderr as utils


def setup_for_stderr(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        ParserForContentsForStderr(),
        utils.TheInstructionDocumentation(instruction_name, 'stderr'))


class ParserForContentsForStderr(utils.ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(actual_files.StderrComparisonActualFile(),
                         utils.StdXActualFileTransformerForEnvVarsReplacement())
