from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.instructions.assert_.process_output.impl import texts
from exactly_lib.impls.instructions.assert_.utils import instruction_of_matcher
from exactly_lib.impls.instructions.assert_.utils.instruction_of_matcher import ModelGetterSdv, FailureMessageConfig, \
    ModelGetter
from exactly_lib.impls.program_execution.processors.store_result_in_files import ExitCodeAndStderrFile
from exactly_lib.impls.text_render import header_rendering
from exactly_lib.impls.types.matcher.impls import property_getters, property_matcher_describers
from exactly_lib.impls.types.matcher.property_getter import PropertyGetter
from exactly_lib.impls.types.matcher.property_matcher import PropertyMatcherSdv
from exactly_lib.impls.types.program import top_lvl_error_msg_rendering
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.type_val_deps.types.integer_matcher import IntegerMatcherSdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering import blocks


def instruction(object_name: str,
                matcher: IntegerMatcherSdv,
                model_getter: ModelGetterSdv[ExitCodeAndStderrFile],
                ) -> AssertPhaseInstruction:
    failure_message_config = _FailureMessageConfig(object_name)
    return instruction_of_matcher.Instruction(
        _exit_code_matcher_from_int_matcher(matcher),
        model_getter,
        failure_message_config
    )


def _exit_code_matcher_from_int_matcher(integer_matcher: IntegerMatcherSdv) -> MatcherSdv[ExitCodeAndStderrFile]:
    return PropertyMatcherSdv(
        integer_matcher,
        property_getters.sdv_of_constant_primitive(_ExitCodePropGetter()),
        property_matcher_describers.IdenticalToMatcher()
    )


class _ExitCodePropGetter(PropertyGetter[ExitCodeAndStderrFile, int]):
    def get_from(self, model: ExitCodeAndStderrFile) -> int:
        return model.exit_code

    def structure(self) -> StructureRenderer:
        return renderers.header_only('unused')


class _FailureMessageConfig(FailureMessageConfig[ExitCodeAndStderrFile]):
    def __init__(self, object_name: str):
        self._object_name = object_name

    def head(self, model_getter: ModelGetter[ExitCodeAndStderrFile], model: ExitCodeAndStderrFile) -> TextRenderer:
        return rend_comb.SingletonSequenceR(
            header_rendering.HeaderValueRenderer.of_unexpected_attr_of_obj(
                texts.ATTRIBUTE__EXIT_CODE,
                self._object_name,
                model_getter.description(),
                'from',
            )
        )

    def tail(self, model_getter: ModelGetter[ExitCodeAndStderrFile], model: ExitCodeAndStderrFile) -> TextRenderer:
        stderr_contents = self._stderr_contents_str(model)
        return rend_comb.SingletonSequenceR(
            blocks.major_block_of_single_minor_block(
                top_lvl_error_msg_rendering.stderr_contents_block(stderr_contents)
            )
        )

    @staticmethod
    def _stderr_contents_str(model: ExitCodeAndStderrFile) -> str:
        with model.stderr.open() as f:
            return std_err_contents.STD_ERR_TEXT_READER.read(f)
