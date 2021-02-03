from typing import Sequence

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.impls.instructions.assert_.process_output.impl import texts
from exactly_lib.impls.instructions.assert_.utils.instruction_of_matcher import ModelGetterSdv, ModelGetter, \
    ModelGetterDdv, ModelGetterAdv, MODEL
from exactly_lib.impls.program_execution.processors.store_result_in_files import ExitCodeAndStderrFile
from exactly_lib.impls.types.path import path_rendering
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable


def model_getter() -> ModelGetterSdv[ExitCodeAndStderrFile]:
    return _ExitCodeGetterSdv()


class _ExitCodeGetter(ModelGetter[ExitCodeAndStderrFile]):
    def __init__(self, tcds: TestCaseDs):
        self._tcds = tcds
        self._sds = tcds.sds

    def description(self) -> SequenceRenderer[MinorBlock]:
        path_ddv = path_ddvs.of_rel_option(
            RelOptionType.REL_RESULT,
            path_ddvs.constant_path_part(self._sds.result.exitcode_file.name),
        )
        described_path = path_ddv.value_of_any_dependency__d(self._tcds)

        return rend_comb.SingletonSequenceR(
            path_rendering.minor_block_renderer_of_primitive(described_path.describer)
        )

    def get(self) -> ExitCodeAndStderrFile:
        return ExitCodeAndStderrFile(
            self._get_exit_code(),
            self._sds.result.stderr_file,
        )

    def _get_exit_code(self) -> int:
        sds = self._sds
        try:
            f = sds.result.exitcode_file.open()
        except IOError:
            rel_path = sds.relative_to_sds_root(sds.result.exitcode_file)
            err_msg = text_docs.single_line(
                str_constructor.FormatMap(
                    'Cannot read {exit_code} from file {file}',
                    {
                        'exit_code': texts.ATTRIBUTE__EXIT_CODE,
                        'file': rel_path,
                    }
                )
            )
            raise HardErrorException(err_msg)
        try:
            contents = f.read()
        except IOError:
            raise HardErrorException(
                text_docs.single_line(
                    str_constructor.Concatenate([
                        _FAILED_TO_READ_CONTENTS_FROM,
                        sds.result.exitcode_file,
                    ])
                ))
        finally:
            f.close()

        try:
            return int(contents)
        except ValueError:
            msg = text_docs.single_line(
                str_constructor.FormatMap(
                    'The contents of the file for {exit_code} ("{file}") is not an integer: "{contents}"',
                    {
                        'exit_code': texts.ATTRIBUTE__EXIT_CODE,
                        'file': sds.result.exitcode_file,
                        'contents': contents,
                    })
            )
            raise HardErrorException(msg)


class _ExitCodeGetterAdv(ModelGetterAdv[ExitCodeAndStderrFile]):
    def __init__(self, tcds: TestCaseDs):
        self._tcds = tcds

    def primitive(self, environment: ApplicationEnvironment) -> ModelGetter[ExitCodeAndStderrFile]:
        return _ExitCodeGetter(self._tcds)


class _ExitCodeGetterDdv(ModelGetterDdv[ExitCodeAndStderrFile]):
    def value_of_any_dependency(self, tcds: TestCaseDs) -> ModelGetterAdv[ExitCodeAndStderrFile]:
        return _ExitCodeGetterAdv(tcds)


class _ExitCodeGetterSdv(ModelGetterSdv[ExitCodeAndStderrFile]):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> ModelGetterDdv[MODEL]:
        return _ExitCodeGetterDdv()


_FAILED_TO_READ_CONTENTS_FROM = 'Failed to read contents from '
