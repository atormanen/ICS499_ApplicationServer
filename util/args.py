from typing import Mapping, Dict, Iterator, Iterable, overload, ItemsView, ValuesView, KeysView, Tuple, Collection


class Command:
    def __init__(self, name, description, action, args: Collection[str] = None):
        self.name = name
        self.description = description
        self.action = action
        self.args = tuple(args) if args is not None else tuple()

    def get_help_msg(self):
        arg_str = ''.join([f' {arg}' for arg in self.args])
        return f"{self.name}{arg_str}: {self.description}"


class CommandDict():

    def __init__(self):
        self._command_dict = {}

    def __eq__(self, o: object) -> bool:
        return self._command_dict.__eq__(o)

    def __ne__(self, o: object) -> bool:
        return self._command_dict.__ne__(o)

    def __repr__(self) -> str:
        return self._command_dict.__repr__()

    def __hash__(self) -> int:
        return self._command_dict.__hash__()

    def __format__(self, format_spec: str) -> str:
        return self._command_dict.__format__(format_spec)

    def __sizeof__(self) -> int:
        return self._command_dict.__sizeof__()

    def clear(self) -> None:
        self._command_dict.clear()

    def copy(self) -> Dict[str, Command]:
        return self._command_dict.copy()

    def popitem(self) -> Tuple[str, Command]:
        return self._command_dict.popitem()

    def setdefault(self, __key: str, __default: Command = ...) -> Command:
        return self._command_dict.setdefault(__key, __default)

    @overload
    def update(self, __m: Mapping[str, Command], **kwargs: Command) -> None: ...

    @overload
    def update(self, __m: Iterable[Tuple[str, Command]], **kwargs: Command) -> None: ...

    @overload
    def update(self, **kwargs: Command) -> None: ...

    def update(self, __m: Mapping[str, Command], **kwargs: Command) -> None:
        self._command_dict.update(__m, **kwargs)

    def keys(self) -> KeysView[str]:
        return self._command_dict.keys()

    def values(self) -> ValuesView[Command]:
        return self._command_dict.values()

    def items(self) -> ItemsView[str, Command]:
        return self._command_dict.items()

    def __len__(self) -> int:
        return self._command_dict.__len__()

    def __getitem__(self, k: str) -> Command:
        return self._command_dict.__getitem__(k)

    def __setitem__(self, k: str, v: Command) -> None:
        self._command_dict.__setitem__(k, v)

    def __delitem__(self, v: str) -> None:
        self._command_dict.__delitem__(v)

    def __iter__(self) -> Iterator[str]:
        return self._command_dict.__iter__()

    def __reversed__(self) -> Iterator[str]:
        return self._command_dict.__reversed__()

    def __str__(self) -> str:
        return self._command_dict.__str__()

    def __or__(self, __value: Mapping[str, Command]) -> Dict[str, Command]:
        return self._command_dict.__or__(__value)

    def __ior__(self, __value: Mapping[str, Command]) -> Dict[str, Command]:
        return self._command_dict.__ior__(__value)

    def add(self, description, args: Collection[str] = None):
        """decorator for a function that is a command"""

        def wrapper(func):
            self[func.__name__] = Command(func.__name__, description, func, args)
            return func

        return wrapper
