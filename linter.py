from os import path
from shlex import quote
import logging
import json

from SublimeLinter import lint

logger = logging.getLogger("SublimeLinter.plugins.phpstan")

class PhpStan(lint.Linter):
    regex = None
    error_stream = lint.STREAM_STDOUT
    default_type = "error"
    multiline = False
    tempfile_suffix = "-"

    defaults = {
        "selector": "embedding.php, source.php"
    }

    def cmd(self):
        cmd = ["phpstan", "analyse"]
        opts = ["--error-format=json", "--no-progress"]

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

    def find_errors(self, output):
        try:
            content = json.loads(output)
        except ValueError:
            logger.error(
                "JSON Decode error: We expected JSON from PHPStan, "
                "but instead got this:\n{}\n\n"
                .format(output)
            )
            self.notify_failure()
            return

        if 'files' not in content:
            return

        for file in content['files']:
            for error in content['files'][file]['messages']:

                error_message = error['message']

                if 'tip' in error:
                    tip = error['tip'].replace("•", "💡")
                    error_message = error_message + "\n\n" + tip

                yield lint.LintMatch(
                    match=error,
                    filename=file,
                    line=error['line'] - 1,
                    col=0,
                    message=error_message,
                    error_type='error',
                    code='',
                )