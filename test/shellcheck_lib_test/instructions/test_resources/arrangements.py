from shellcheck_lib.test_case.os_services import OsServices, new_default
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.test_resources import file_structure


class ActEnvironment(tuple):
    def __new__(cls,
                home_and_eds: i.HomeAndEds):
        return tuple.__new__(cls, (home_and_eds,))

    @property
    def home_and_eds(self) -> i.HomeAndEds:
        return self[0]


class ActResultProducer:
    def __init__(self, act_result: utils.ActResult = utils.ActResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> utils.ActResult:
        return self.act_result


class ArrangementBase:
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 ):
        self.home_contents = home_contents


class ArrangementWithEds(ArrangementBase):
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents: eds_populator.EdsPopulator = eds_populator.empty(),
                 os_services: OsServices = new_default(),
                 ):
        super().__init__(home_contents)
        self.eds_contents = eds_contents
        self.os_services = os_services


class ArrangementPostAct(ArrangementWithEds):
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents: eds_populator.EdsPopulator = eds_populator.empty(),
                 act_result_producer: ActResultProducer = ActResultProducer(),
                 os_services: OsServices = new_default()
                 ):
        super().__init__(home_contents, eds_contents, os_services)
        self.act_result_producer = act_result_producer
