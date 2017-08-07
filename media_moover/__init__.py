# -*- coding: utf-8 -*-
import os
from os.path import join,exists
import os

DEFAULT_SOURCE = '/home/kostya/Входящие'
DEFAULT_DESTANATION = '/home/kostya/Исходящие'

def file_list(path, ext):
    return [f for f in os.listdir(path) if f.lower().endswith(ext)]


def validate_paths(source, destanation):
    if not os.path.exists(source):
        raise ValueError("Нужен правильный исходный каталог")

    if not os.path.exists(destanation):
        raise ValueError("Нужен правильный каталог назанчения")

    if source==destanation:
        raise ValueError("Пути должны быть различные")

