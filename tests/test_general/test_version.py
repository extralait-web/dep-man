from packaging.version import parse as parse_version

import dep_man
from dep_man.version import version_info


def test_version_info():
    version_info_fields = [
        "dep_man version",
        "python version",
        "platform",
        "related packages",
        "commit",
    ]

    version_info_string = version_info()
    assert all(f"{field}:" in version_info_string for field in version_info_fields)
    assert version_info_string.count("\n") == 4


def test_standard_version():
    v = parse_version(dep_man.VERSION)
    assert str(v) == dep_man.VERSION


def test_version_attribute_is_present():
    assert hasattr(dep_man, "__version__")


def test_version_attribute_is_a_string():
    assert isinstance(dep_man.__version__, str)
