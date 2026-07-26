#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import types
import inspect


class Method:
    def __init__(self):
        self.methods = {}

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return types.MethodType(self, instance)

    def register(self, func):
        sig = inspect.signature(func)
        typ = tuple()
        for name, parm in sig.parameters.items():
            if name == "self":
                continue
            if parm.annotation is inspect._empty:
                raise TypeError(f"{name!r}: All parameters must be annotated")
            if parm.default != inspect._empty:
                self.methods[typ] = func
            typ = typ + (parm.annotation,)
        self.methods[typ] = func

    def __call__(self, *args, **kwargs):
        typ = tuple(type(a) for a in args[1:])
        return self.methods[typ](*args)


class MultiDict(dict):
    def __setitem__(self, key, func):
        if key[:2] == "__" and key[-2:] == "__":
            super().__setitem__(key, func)
        else:
            mm = self.setdefault(key, Method())
            mm.register(func)


class MultiMeta(type):
    @classmethod
    def __prepare__(name, bases, ns):
        return MultiDict()


class Add(metaclass=MultiMeta):
    def add(self, x: int, y: int) -> int:
        return x + y

    def add(self, x: str, y: str) -> str:  # noqa: F811
        return x + "__" + y

    def add(self, x: float, y: float = 10.0) -> float:  # noqa: F811
        return x + y


if __name__ == "__main__":
    a = Add()
    print(a.add(10, 12))
    print(a.add("as", "df"))
    print(a.add(10.3))
