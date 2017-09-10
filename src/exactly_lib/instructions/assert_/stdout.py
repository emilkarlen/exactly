from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents import stdout_stderr as utils


def setup_for_stdout(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(),
        utils.TheInstructionDocumentation(instruction_name, 'stdout'))


def parser() -> utils.ParserForContentsForActualValue:
    return utils.ParserForContentsForActualValue(actual_files.StdoutComparisonActualFile())
