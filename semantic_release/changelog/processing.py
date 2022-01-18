from ..changelog import handlers
from ..helpers import import_path
from ..settings import config


def get_body_handler():
    body_handler = handlers.noop
    for handler in config.get("changelog_body_handlers", "").split(","):
        handler = handler.strip()
        if handler:
            body_handler |= getattr(handlers, handler, None) or import_path(handler)
    return body_handler


def get_subject_handler():
    subject_handler = handlers.noop
    for handler in config.get("changelog_subject_handlers", "").split(","):
        handler = handler.strip()
        if handler:
            subject_handler |= getattr(handlers, handler, None) or import_path(handler)
    return subject_handler


def changelog_processing(
    owner: str, repo_name: str, changelog: list, changelog_sections: list, **kwargs
):
    """Processing subject and body.

    It will work only with `commit_analyzer=semantic_release.history.logs.get_commits`
    """
    subject_handler = get_subject_handler()
    body_handler = get_body_handler()
    for commit in changelog:
        commit["subject"] = subject_handler(commit["subject"])
        commit["body"] = commit["body"] and body_handler(commit["body"]) or commit["body"]

    return ""
