from typing import Sequence

from exactly_lib.impls.types.string_transformer.impl import identity, sequence
from exactly_lib.type_val_deps.types.string_transformer import ddvs
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv


def resolve(unknown_num_transformers: Sequence[StringTransformerDdv]) -> StringTransformerDdv:
    num_transformers = len(unknown_num_transformers)

    if num_transformers == 0:
        return ddvs.StringTransformerConstantDdv(identity.IdentityStringTransformer())
    elif num_transformers == 1:
        return unknown_num_transformers[0]
    else:
        return sequence.StringTransformerSequenceDdv(unknown_num_transformers)
