from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.file_utils.std import StdOutputFiles


class ParseException(Exception):
    def __init__(self, cause: TextRenderer):
        self.cause = cause

    @staticmethod
    def of_str(cause: str) -> 'ParseException':
        return ParseException(text_docs.single_pre_formatted_line_object(cause))


class ActionToCheck(SymbolUser):
    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        pre-sds validation of the source that this object represents.

        If success is not returned, then the test is aborted.

        :raises: :class:`HardErrorException`
        """
        raise NotImplementedError()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        """
        post-setup validation of the source that this object represents.

        If success is not returned, then the test is aborted.

        :raises: :class:`HardErrorException`
        """
        raise NotImplementedError()

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        """
        Executed after validate.

        An opportunity to prepare for execution.

        E.g. write the source code to file.

        :raises: :class:`HardErrorException`
        """
        raise NotImplementedError()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                atc_input: AtcExecutionInput,
                output_files: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        """
        Executed after prepare.

        :returns exit code of executed program, or error

        :raises: :class:`HardErrorException`
        """
        raise NotImplementedError()


class Actor(ABC):
    """
    Parses the contents of the act phase which is the source that is to be executed as the act phase.
    (after it has been extracted from the test case file).

    Does syntax checking/validation while parsing - and reports syntax errors
    in terms of exceptions.
    """

    @abstractmethod
    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        """
        :raises ParseException
        """
        pass
