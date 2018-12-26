from os import path
from shlex import quote

from SublimeLinter.lint import Linter


class PhpStan(Linter):
    regex = r"^(?!Note: ).*:(?P<line>[0-9]+):(?P<message>.+)"
    default_type = "error"
    multiline = False
    tempfile_suffix = "-"
    defaults = {
        "selector": "source.php",
        "use_composer_autoload": True,
        "--level": "max",
    }

    def cmd(self):
        settings = self.get_view_settings()

        cmd = ["phpstan", "analyse"]
        opts = ["--error-format=raw", "--no-progress"]

        if settings.get("use_composer_autoload", True):
            autoload_file = self.find_autoload_php(self.view.file_name())
            if autoload_file:
                opts.append("--autoload-file={}".format(quote(autoload_file)))

        return cmd + opts + ["${args}", "--", "${file}"]

    def find_autoload_php(self, file_path):
        basedir = None
        while file_path:
            basedir = path.dirname(file_path)
            composer_json = "{basedir}/composer.json".format(basedir=basedir)
            composer_lock = "{basedir}/composer.lock".format(basedir=basedir)
            autoload = "{basedir}/vendor/autoload.php".format(basedir=basedir)
            if path.isfile(autoload) and (
                path.isfile(composer_json) or path.isfile(composer_lock)
            ):
                return autoload
            if basedir == file_path:
                break
            file_path = basedir
