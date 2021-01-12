from typing import Sequence

from exactly_lib.impls.types.string_transformer.impl import identity, sequence
from exactly_lib.type_val_prims.string_transformer import StringTransformer


def resolve(unknown_num_transformers: Sequence[StringTransformer]) -> StringTransformer:
    num_transformers = len(unknown_num_transformers)

    if num_transformers == 0:
        return identity.IdentityStringTransformer()
    elif num_transformers == 1:
        return unknown_num_transformers[0]
    else:
        return sequence.SequenceStringTransformer(unknown_num_transformers)
