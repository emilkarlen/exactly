from typing import Iterator, List

from exactly_lib.type_system.logic.impls.transformed_string_models import TransformedStringModelFromLines
from exactly_lib.type_system.logic.string_model import StringModel


class Empty(TransformedStringModelFromLines):
    def __init__(self, transformed: StringModel):
        super().__init__(
            self._transform,
            transformed,
            False,
        )

    @staticmethod
    def _transform(lines: Iterator[str]) -> Iterator[str]:
        return iter(())


class SingleNonNegIntModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 zero_based_line_num: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._zero_based_line_num = zero_based_line_num

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        requested = self._zero_based_line_num
        current = 0
        for line in lines:
            if requested == current:
                yield line
                break
            else:
                current += 1


class SingleNegIntModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 neg_line_num: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._neg_line_num = neg_line_num
        self._pocket_size = abs(neg_line_num)

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pocket = _filled_pocket(self._pocket_size, lines)

        if len(pocket) < self._pocket_size:
            return

        for next_line in lines:
            del pocket[0]
            pocket.append(next_line)

        yield pocket[0]


class UpperNonNegLimitModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 zero_based_upper_limit: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._zero_based_upper_limit = zero_based_upper_limit

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        limit = self._zero_based_upper_limit
        current = 0

        for line in lines:
            yield line
            if limit == current:
                return
            current += 1


class UpperNegLimitModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 neg_line_num: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._neg_line_num = neg_line_num

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pocket_size = abs(self._neg_line_num)
        pocket = _filled_pocket(pocket_size, lines)

        if len(pocket) < pocket_size:
            return

        yield pocket[0]

        for next_line in lines:
            del pocket[0]
            pocket.append(next_line)

            yield pocket[0]


class LowerNonNegLimitModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 zero_based_lower_limit: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._zero_based_lower_limit = zero_based_lower_limit

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        _skip(self._zero_based_lower_limit, lines)

        for line in lines:
            yield line


class LowerNegLimitModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 neg_line_num: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._neg_line_num = neg_line_num

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pocket_size = abs(self._neg_line_num)
        pocket = _filled_pocket(pocket_size, lines)

        for next_line in lines:
            del pocket[0]
            pocket.append(next_line)

        for line in pocket:
            yield line


class LowerNonNegUpperNonNegModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 zero_based_lower_limit: int,
                 zero_based_upper_limit: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._zero_based_lower_limit = zero_based_lower_limit
        self._zero_based_upper_limit = zero_based_upper_limit

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        _skip(self._zero_based_lower_limit, lines)
        num_requested = self._zero_based_upper_limit - self._zero_based_lower_limit + 1

        for line in _limited(lines, num_requested):
            yield line


class LowerNonNegUpperNegModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 zero_based_lower_limit: int,
                 neg_upper_limit: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._zero_based_lower_limit = zero_based_lower_limit
        self._neg_upper_limit = neg_upper_limit

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        upper_len = abs(self._neg_upper_limit)

        pocket = _filled_pocket(upper_len, lines)

        if len(pocket) < upper_len:
            return

        if not self._forward_pocket_to_lower_limit(pocket, lines):
            return

        yield pocket[0]
        for line in lines:
            del pocket[0]
            pocket.append(line)
            yield pocket[0]

    def _forward_pocket_to_lower_limit(self, pocket: List[str], lines: Iterator[str]) -> bool:
        left_to_consume = self._zero_based_lower_limit

        for next_line in _limited(lines, left_to_consume):
            del pocket[0]
            pocket.append(next_line)
            left_to_consume -= 1

        return left_to_consume == 0


class LowerNegUpperNonNegModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 neg_lower_limit: int,
                 zero_based_upper_limit: int,
                 ):
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._neg_lower_limit = neg_lower_limit
        self._zero_based_upper_limit = zero_based_upper_limit

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        upper = self._zero_based_upper_limit
        lower_len = abs(self._neg_lower_limit)

        pocket = _filled_pocket(lower_len, lines)

        pocket_1st_idx = 0
        for line in lines:
            del pocket[0]
            pocket.append(line)

            pocket_1st_idx += 1
            if pocket_1st_idx > upper:
                return

        num_to_produce = upper - pocket_1st_idx + 1

        for line in pocket:
            if num_to_produce == 0:
                return
            yield line
            num_to_produce -= 1


class LowerNegUpperNegModel(TransformedStringModelFromLines):
    def __init__(self,
                 transformed: StringModel,
                 neg_lower_limit: int,
                 neg_upper_limit: int,
                 ):
        """
        neg_lower_limit < neg_upper_limit
        """
        super().__init__(
            self._transform,
            transformed,
            False,
        )
        self._neg_lower_limit = neg_lower_limit
        self._neg_upper_limit = neg_upper_limit

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        lower_len = abs(self._neg_lower_limit)
        upper_len = abs(self._neg_upper_limit)

        pocket = _filled_pocket(lower_len, lines)

        num_non_existing_at_head = lower_len - len(pocket)
        if num_non_existing_at_head != 0:
            lower_len -= num_non_existing_at_head
            if upper_len > lower_len:
                return

        for line in lines:
            del pocket[0]
            pocket.append(line)

        num_to_produce = lower_len - upper_len + 1

        for line in pocket:
            if num_to_produce == 0:
                return
            yield line
            num_to_produce -= 1


def _limited(iterator: Iterator[str], size: int) -> Iterator[str]:
    if size == 0:
        return
    for e in iterator:
        yield e
        size -= 1
        if size == 0:
            return


def _skip(num_lines: int, lines: Iterator[str]):
    for _ in _limited(lines, num_lines):
        pass


def _filled_pocket(size: int, lines: Iterator[str]) -> List[str]:
    if size == 0:
        return []

    ret_val = []

    for line in lines:
        ret_val.append(line)
        if len(ret_val) == size:
            break

    return ret_val
