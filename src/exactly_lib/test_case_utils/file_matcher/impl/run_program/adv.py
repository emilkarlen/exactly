from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherImplBase, FileMatcherAdvImplBase
from exactly_lib.test_case_utils.program.execution import exe_wo_transformation
from exactly_lib.test_case_utils.program.execution.exe_wo_transformation import ExecutionResultAndStderr
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.program.program import Program, ProgramAdv
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class Matcher(FileMatcherImplBase):
    NAME = ' '.join((file_matcher.PROGRAM_MATCHER_NAME,
                     syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 application_environment: ApplicationEnvironment,
                 matcher_program: Program,
                 ):
        self._application_environment = application_environment
        self._matcher_program = matcher_program

    @staticmethod
    def new_structure_tree(program: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Matcher.NAME,
            None,
            (custom_details.TreeStructure(program),),
            (),
        )

    @property
    def name(self) -> str:
        return self.NAME

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        app_env = self._application_environment
        program_for_model = self._program_for_model(model)
        exe_result = exe_wo_transformation.execute(
            program_for_model,
            app_env.tmp_files_space.new_path_as_existing_dir(),
            app_env.os_services,
            app_env.process_execution_settings,
        )
        return MatchingResult(
            exe_result.exit_code == 0,
            _ResultRenderer(self._new_tb(program_for_model),
                            exe_result)
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._matcher_program.structure())

    def _program_for_model(self, model: FileMatcherModel) -> Program:
        program = self._matcher_program
        command_for_model = program.command.new_with_appended_arguments([str(model.path.primitive)])
        return Program(
            command_for_model,
            program.stdin,
            program.transformation,
        )

    def _new_tb(self, program: Program) -> TraceBuilder:
        return TraceBuilder(self.NAME).append_details(custom_details.TreeStructure(program.structure()))


class _ResultRenderer(NodeRenderer[bool]):
    OUTPUT_ON_STDERR_HEADER = 'Output on ' + misc_texts.STDERR
    EXIT_CODE_HEADER = misc_texts.EXIT_CODE_TITLE

    def __init__(self,
                 trace_builder_w_program_spec: TraceBuilder,
                 result: ExecutionResultAndStderr,
                 ):
        self._trace_builder = trace_builder_w_program_spec
        self._result = result

    def render(self) -> Node[bool]:
        exit_code = self._result.exit_code
        tb = self._trace_builder

        tb.append_details(
            custom_details.actual__custom(
                self.EXIT_CODE_HEADER,
                details.String(exit_code),
            )
        )
        if exit_code != 0 and self._result.stderr_contents:
            tb.append_details(
                details.HeaderAndValue(
                    self.OUTPUT_ON_STDERR_HEADER,
                    details.PreFormattedString(self._result.stderr_contents),
                )
            )

        return tb.build_bool(exit_code == 0).render()


class Adv(FileMatcherAdvImplBase):
    def __init__(self, program: ProgramAdv):
        self._program = program

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[FileMatcherModel]:
        return Matcher(
            environment,
            self._program.primitive(environment)
        )
