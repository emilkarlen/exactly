from enum import Enum

EXIT_CODE_FILE_NAME = 'exit-code'

STDOUT_FILE_NAME = 'stdout'
STDERR_FILE_NAME = 'stderr'


class ProcOutputFile(Enum):
    STDOUT = 1
    STDERR = 2


PROC_OUTPUT_FILE_NAMES = {
    ProcOutputFile.STDOUT: STDOUT_FILE_NAME,
    ProcOutputFile.STDERR: STDERR_FILE_NAME,
}


class FileNames:
    @property
    def exit_code(self) -> str:
        return EXIT_CODE_FILE_NAME

    @property
    def stdout(self) -> str:
        return STDOUT_FILE_NAME

    @property
    def stderr(self) -> str:
        return STDERR_FILE_NAME

    @staticmethod
    def name_of(output_file: ProcOutputFile) -> str:
        return PROC_OUTPUT_FILE_NAMES[output_file]


FILE_NAMES = FileNames()
