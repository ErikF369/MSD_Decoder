load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Verwende rules_python Version 0.36.0
http_archive(
    name = "rules_python",
    urls = ["https://github.com/bazelbuild/rules_python/releases/download/0.36.0/rules_python-0.36.0.tar.gz"],
    sha256 = "ca77768989a7f311186a29747e3e95c936a41dffac779aff6b443db22290d913",
)

# Lade pip_install, um Python-Abhängigkeiten zu verwalten
load("@rules_python//rules_python:pip.bzl", "pip_install")

pip_install(
    requirements = "//:requirements.txt",
)