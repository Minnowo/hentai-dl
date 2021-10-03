# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.

import sys
import os.path


def list_dirs(path : str) -> list:
    """List directories in the given directory"""
    current_directory = os.getcwd()
    try:
        os.chdir(path)
        return next(os.walk('.'))[1]
    finally:
        os.chdir(current_directory)


def create_directory_from_file_name(path : str) -> bool:
    """
    Creates a directory from the file path.

    Returns: 
        True if the path was created
        
        False if path was not created
    """
    return create_directory(os.path.dirname(path))


def create_directory(path : str) -> bool:
    """
    Creates the given directory.

    Returns: 
        True if the path was created
        
        False if path was not created
    """
    try:
        os.makedirs(path)
    except OSError:
        pass
    return os.path.isdir(path)


def remove_file(path : str) -> bool:
    """
    Deletes the given file.

    Returns: 
        True if the file was removed
        
        False if file was not removed
    """
    try:
        os.unlink(path)
    except OSError:
        pass
    return not os.path.exists(path)


def remove_directory(path : str) -> bool:
    """
    Deletes the given directory.

    Returns: 
        True if the path was removed

        False if path was not removed
    """
    try:
        os.rmdir(path)
    except OSError:
        pass
    return not os.path.isdir(path)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # No resource path found, returns path relative to current file
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)