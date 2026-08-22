from collections.abc import Callable


def awaited(func: Callable) -> Callable:
    func.__annotations__ = {
        name: hint for name, hint in func.__annotations__.items() if name != "return"
    }
    return func
