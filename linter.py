from SublimeLinter.lint import Linter


class PhpStan(Linter):
    cmd = (
        "phpstan",
        "analyse",
        "--errorFormat=raw",
        "--no-progress",
        "${args}",
        "${file}",
    )
    regex = r"^(?!Note: ).*:(?P<line>[0-9]+):(?P<message>.+)"
    default_type = "error"
    multiline = False
    tempfile_suffix = "-"
    defaults = {
        "selector": "source.php",
        "--autoload-file": "${file}",
        "--level": "max",
    }
