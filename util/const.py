from typing import Tuple, Dict


class ConstContainer:
    """By inheriting from this class, all class constants stored with capitalized
    names will be accessible as a collection via class methods."""

    @classmethod
    def _is_good_item(cls, k: str):
        return k.isupper()

    # noinspection PyTypeChecker
    @classmethod
    def values(cls) -> Tuple[str]:
        """Gets a list of all values."""
        return tuple([v for (k, v) in vars(cls).items() if cls._is_good_item(k)])

    # noinspection PyTypeChecker
    @classmethod
    def items(cls) -> Dict[str, str]:
        """Gets a list of all key-value pairs."""
        return [(k, v) for (k, v) in vars(cls).items() if cls._is_good_item(k)]

    # noinspection PyTypeChecker
    @classmethod
    def keys(cls) -> Tuple[str]:
        """Gets a list of all constant names."""

        return tuple([k for (k, v) in vars(cls).items() if cls._is_good_item(k)])
