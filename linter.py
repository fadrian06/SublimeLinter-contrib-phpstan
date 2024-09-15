from os import path
from shlex import quote
import logging

from SublimeLinter import lint

logger = logging.getLogger("SublimeLinter.plugins.phpstan")

class PhpStan(lint.Linter):
    regex = r"^(?!Note: ).*:(?P<line>[0-9]+):(?P<message>.+)"
    error_stream = lint.STREAM_STDOUT
    default_type = "error"
    multiline = False
    tempfile_suffix = "php"

    defaults = {
        "enable_cells": True,
        "selector": "source.php",
        "lint_mode": "background"
    }

    def cmd(self):
        cmd = ["phpstan", "analyse"]
        opts = ["--error-format=raw", "--no-progress"]

        configPath = self.find_phpstan_configuration(self.view.file_name())

        if configPath:
            opts.append("--configuration={}".format(quote(configPath)))

        autoload_file = self.find_autoload_php(configPath)

        if autoload_file:
            opts.append("--autoload-file={}".format(quote(autoload_file)))

            cmd[0] = autoload_file.replace("/autoload.php", "/bin/phpstan")

        return cmd + ["${args}"] + opts + ["--", "${file}"]

    def find_autoload_php(self, configPath):
        pathAutoLoad = configPath.replace("/phpstan.neon", "/vendor/autoload.php")

        if (path.isfile(pathAutoLoad)):
            return pathAutoLoad

        return None

    def find_phpstan_configuration(self, file_path):
        basedir = None
        while file_path:
            basedir = path.dirname(file_path)
            configFiles = (
                "{basedir}/phpstan.neon".format(basedir=basedir),
                "{basedir}/phpstan.neon.dist".format(basedir=basedir),
            )

            for configFile in configFiles:
                if (path.isfile(configFile)):
                    return configFile

            if (basedir == file_path):
                break

            file_path = basedir
