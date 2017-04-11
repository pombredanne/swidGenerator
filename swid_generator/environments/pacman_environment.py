# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import subprocess

from .common import CommonEnvironment
from ..package_info import PackageInfo, FileInfo


class PacmanEnvironment(CommonEnvironment):
    """
    Environment class for distributions using pacman as package manager (used
    by Arch Linux).

    """
    executable = 'pacman'

    @classmethod
    def get_package_list(cls):
        """
        Get list of installed packages.

        Returns:
            List of ``PackageInfo`` instances.

        """

        command_args = [cls.executable, '-Q', '--color', 'never']
        data = subprocess.check_output(command_args)
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        lines = filter(None, data.rstrip().split('\n'))
        result = []
        for line in lines:
            split_line = line.split()
            assert len(split_line) == 2, repr(split_line)
            info = PackageInfo()
            info.package = split_line[0]
            info.version = split_line[1]
            result.append(info)
        return result

    @classmethod
    def get_files_for_package(cls, package_info):
        """
        Get list of files related to the specified package.

        Caching could be implemented by using `Ql` without any package name.

        Args:
            package_name (str):
                The package name as string (e.g. ``cowsay``).

        Returns:
            List of ``FileInfo`` instances.

        """
        command_args = [cls.executable, '-Ql', package_info.package]
        data = subprocess.check_output(command_args)
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        lines = filter(None, data.rstrip().split('\n'))
        result = []
        for line in lines:
            split_line = line.split(' ', 1)
            assert len(split_line) == 2, repr(split_line)
            file_path = split_line[1]
            if cls._is_file(file_path):
                file_info = FileInfo(file_path)
                # With the assumption that files in the '/etc'-Folders are mostly Configuration-Files
                if "/etc" in file_path:
                    file_info.mutable = True
                result.append(file_info)
        return result

    @classmethod
    def get_files_from_packagefile(cls, file_fullpathname):

        command_args = [cls.executable, '-Qlp', file_fullpathname]
        data = subprocess.check_output(command_args)
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        save_options = cls._create_temp_folder(file_fullpathname)
        lines = data.split('\n')

        lines = filter(lambda l: len(l) > 0, lines)

        for line in lines:
            split_line = line.split(' ')

        return []

    @classmethod
    def get_packageinfo_from_packagefile(cls, file_path):
        command_args = [cls.executable, '--query', '--file', file_path]
        data = subprocess.check_output(command_args)
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        line_split = data.split(' ')

        package_info = PackageInfo()
        package_info.package = line_split[0]
        package_info.version = line_split[1].rstrip()

        return package_info
