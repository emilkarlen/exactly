from typing import Sequence

from exactly_lib.impls.types.string_transformer import sequence_resolving_ddv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from . import ddvs


class ConstantStringStringSourceSdv(StringSourceSdv):
    def __init__(self, string: StringSdv):
        self._string = string

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        return ddvs.ConstantStringStringSourceDdv(self._string.resolve(symbols))


class PathStringSourceSdv(StringSourceSdv):
    def __init__(self, path: PathSdv):
        self._path = path

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._path.references

    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        return ddvs.PathStringSourceDdv(self._path.resolve(symbols))


class ProgramOutputStringSourceSdv(StringSourceSdv):
    def __init__(self,
                 structure_header: str,
                 ignore_exit_code: bool,
                 output_channel_to_capture: ProcOutputFile,
                 program: ProgramSdv,
                 ):
        self._structure_header = structure_header
        self._ignore_exit_code = ignore_exit_code
        self._output_channel_to_capture = output_channel_to_capture
        self._program = program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references

    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        program_ddv = self._program.resolve(symbols)
        command_source_ddv = ddvs.CommandOutputStringSourceDdv(
            self._structure_header,
            self._ignore_exit_code,
            self._output_channel_to_capture,
            program_ddv.command,
            program_ddv.stdin,
        )
        return (
            ddvs.TransformedStringSourceDdv(command_source_ddv,
                                            sequence_resolving_ddv.resolve(program_ddv.transformations))
            if program_ddv.transformations
            else
            command_source_ddv
        )


class TransformedStringSourceSdv(StringSourceSdv):
    def __init__(self,
                 transformed: StringSourceSdv,
                 transformer: StringTransformerSdv,
                 ):
        self._transformed = transformed
        self._transformer = transformer
        self._references = tuple(self._transformed.references) + tuple(self._transformer.references)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        return ddvs.TransformedStringSourceDdv(self._transformed.resolve(symbols),
                                               self._transformer.resolve(symbols))
