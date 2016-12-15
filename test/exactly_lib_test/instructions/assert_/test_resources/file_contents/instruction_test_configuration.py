from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import sds_populator


class HomeOrSdsPopulator:
    def __init__(self, populator):
        self.populator = populator

    def apply(self, home_and_sds: HomeAndSds):
        if isinstance(self.populator, file_structure.DirContents):
            self.populator.write_to(home_and_sds.home_dir_path)
        if isinstance(self.populator, sds_populator.SdsPopulator):
            self.populator.apply(home_and_sds.sds)

    @property
    def home_populator(self) -> file_structure.DirContents:
        """"
        :return None iff populator is not an `DirContents`
        """
        if isinstance(self.populator, file_structure.DirContents):
            return self.populator
        else:
            return None

    @property
    def sds_populator(self) -> sds_populator.SdsPopulator:
        """"
        :return None iff populator is not an `SdsPopulator`
        """
        if isinstance(self.populator, sds_populator.SdsPopulator):
            return self.populator
        else:
            return None


class TestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        raise NotImplementedError()

    def empty_arrangement(self) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct()

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()
