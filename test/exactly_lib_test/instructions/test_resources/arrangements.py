from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.util.process_execution.process_execution_settings import with_no_timeout
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import sds_populator, utils


class ActEnvironment(tuple):
    def __new__(cls,
                home_and_sds: i.HomeAndSds):
        return tuple.__new__(cls, (home_and_sds,))

    @property
    def home_and_sds(self) -> i.HomeAndSds:
        return self[0]


class ActResultProducer:
    def __init__(self, act_result: utils.ActResult = utils.ActResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> utils.ActResult:
        return self.act_result


class ArrangementBase:
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 environ: dict = None,
                 ):
        self.home_contents = home_contents
        self.environ = {} if environ is None else environ


class ArrangementWithSds(ArrangementBase):
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 os_services: OsServices = new_default(),
                 environ: dict = None,
                 process_execution_settings=with_no_timeout(),
                 ):
        super().__init__(home_contents, environ)
        self.sds_contents = sds_contents
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings


class ArrangementPostAct(ArrangementWithSds):
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 act_result_producer: ActResultProducer = ActResultProducer(),
                 os_services: OsServices = new_default(),
                 environ: dict = None,
                 process_execution_settings=with_no_timeout(),
                 ):
        super().__init__(home_contents, sds_contents, os_services, environ, process_execution_settings)
        self.act_result_producer = act_result_producer
