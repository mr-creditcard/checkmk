load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")

py_library(
    name = "cmk_product_usage",
    srcs = glob(["**/*.py"]),
    imports = ["../.."],
    visibility = ["//cmk:__subpackages__"],
    deps = [
        "//cmk/utils:cmk_utils",
        "//packages/cmk-ccc:version",
        "//packages/cmk-livestatus-client:py_livestatus",
        requirement("requests"),
        requirement("werkzeug"),
    ],
)
