import mock
import pytest

from semantic_release.vcs_helpers import get_repository_owner_and_name

from . import *

owner, name = get_repository_owner_and_name()


@pytest.mark.parametrize(
    "message,expected_output",
    [
        (
            "test (#123)",
            f"test ([#123](https://gitlab.com/{owner}/{name}/-/issues/123))",
        ),
        ("test without commit", "test without commit"),
    ],
)
def test_add_mr_link_gitlab(message, expected_output):
    with mock.patch(
        "semantic_release.vcs_helpers.get_repository_owner_and_name",
        return_value=[owner, name],
    ):
        from semantic_release.history.processors import add_mr_link_gitlab

        assert add_mr_link_gitlab(message) == expected_output


@pytest.mark.parametrize(
    "message,expected_output",
    [
        ("test (#123)", f"test ([#123](https://github.com/{owner}/{name}/issues/123))"),
        ("test without commit", "test without commit"),
        ("test (#123) in middle", "test (#123) in middle"),
    ],
)
def test_add_pr_link_github(message, expected_output):
    with mock.patch(
        "semantic_release.vcs_helpers.get_repository_owner_and_name",
        return_value=[owner, name],
    ):
        from semantic_release.history.processors import add_pr_link_github

        assert add_pr_link_github(message) == expected_output


@pytest.mark.parametrize(
    "message,expected_output",
    [
        ("test", "Test"),
        ("Test", "Test"),
        ("tesT", "TesT"),
    ],
)
def test_capitalize(message, expected_output):
    from semantic_release.history.processors import capitalize

    assert capitalize(message) == expected_output


@pytest.mark.parametrize(
    "message,expected_output",
    [
        ("test", "test."),
        ("test.", "test."),
        ("test:", "test:"),
    ],
)
def test_final_dot(message, expected_output):
    from semantic_release.history.processors import final_dot

    assert final_dot(message) == expected_output


@pytest.mark.parametrize(
    "message,expected_output",
    [
        (" test ", "test"),
        ("test\n", "test"),
        ("test", "test"),
    ],
)
def test_strip(message, expected_output):
    from semantic_release.history.processors import strip

    assert strip(message) == expected_output


@pytest.mark.parametrize(
    "message,first,expected_output",
    [
        ("- Sample text\n\nwithout ident", None, "  - Sample text\n\n  without ident"),
        (
            "- Sample text\n\n  without ident",
            None,
            "  - Sample text\n\n    without ident",
        ),
        ("Sample text\n\nwithout ident", "- ", "- Sample text\n\n  without ident"),
    ],
)
def test_indent(message, first, expected_output):
    from semantic_release.history.processors import indent

    assert indent(message, first=first) == expected_output


def test_noop():
    from semantic_release.history.processors import noop

    assert noop("123") == "123"


def test_drop():
    from semantic_release.history.processors import drop

    assert drop("123") == ""


def test_repr_or():
    from semantic_release.history.processors import strip, add_mr_link_gitlab

    proc = strip | add_mr_link_gitlab
    assert repr(proc) == "'strip | add_mr_link_gitlab'"
    assert proc(' test ') == "test"
