import json
from typing import Any, Dict


def json_encode(value: Any) -> str:
    """Encode given value to JSON."""

    return json.dumps(value, default=encode_to_json)


def json_decode(s: str) -> Any:
    """Decode given JSON to a value."""

    return json.loads(s, object_hook=decode_from_json)


def json_serializable(cls):
    """Mark a class as a JSON serializable class."""

    _register_cls(cls)

    class Serializable(cls):
        """A class that can be serialized to JSON."""

        def __init_subclass__(cls, /, **kwargs) -> None:
            super().__init_subclass__(**kwargs)

            _register_cls(cls)

    Serializable.__name__ = cls.__name__

    return Serializable


def encode_to_json(o: Any) -> Dict[str, Any]:
    """Encode a serializable object to its JSON representation."""

    clsname = o.__class__.__name__

    if clsname in _json_types_registry:
        return {
            "__json_result__": _json_types_registry[clsname].to_json(o),
            "__json_result_type__": clsname,
        }

    raise TypeError(f"Object of type {clsname} is not JSON serializable")


def decode_from_json(d: Dict[str, Any]) -> Any:
    """Decode a serializable object from its JSON representation."""

    if "__json_result__" in d and "__json_result_type__" in d:
        clsname = d["__json_result_type__"]

        if clsname in _json_types_registry:
            return _json_types_registry[clsname].from_json(d["__json_result__"])

    return d


_json_types_registry: Dict[str, Any] = {}


def _register_cls(cls) -> None:
    if not hasattr(cls, "to_json") or not callable(cls.to_json):
        raise TypeError(
            f"Class {cls.__name__} was marked as JSON serializable but does not implement to_json classmethod"
        )

    if not hasattr(cls, "from_json") or not callable(cls.from_json):
        raise TypeError(
            f"Class {cls.__name__} was marked as JSON serializable but does not implement from_json classmethod"
        )

    _json_types_registry[cls.__name__] = cls
