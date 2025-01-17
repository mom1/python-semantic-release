"""Logs
"""
import logging
from typing import Optional

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction, import_path
from ..settings import config, current_commit_parser
from ..vcs_helpers import get_commit_log, get_commits_for_chagelog
from . import processors
from .parser_helpers import ParsedCommit

logger = logging.getLogger(__name__)

LEVELS = {
    0: None,
    1: "patch",
    2: "minor",
    3: "major",
}


@LoggedFunction(logger)
def evaluate_version_bump(current_version: str, force: str = None) -> Optional[str]:
    """
    Read git log since the last release to decide if we should make a major, minor or patch release.

    :param current_version: A string with the current version number.
    :param force: A string with the bump level that should be forced.
    :return: A string with either major, minor or patch if there should be a release.
             If no release is necessary, None will be returned.
    """
    if force:
        return force

    bump = None

    changes = []
    commit_count = 0

    for _, commit_message in get_commit_log(current_version):
        if commit_message.startswith(current_version):
            # Stop once we reach the current version
            # (we are looping in the order of newest -> oldest)
            logger.debug(
                f'"{commit_message}" is commit for {current_version}, breaking loop'
            )
            break

        commit_count += 1

        # Attempt to parse this commit using the currently-configured parser
        try:
            message = current_commit_parser()(commit_message)
            changes.append(message.bump)
        except UnknownCommitMessageStyleError as err:
            logger.debug(f"Ignoring UnknownCommitMessageStyleError: {err}")
            pass

    logger.debug(f"Commits found since last release: {commit_count}")

    if changes:
        # Select the largest required bump level from the commits we parsed
        level = max(changes)
        if level in LEVELS:
            bump = LEVELS[level]
        else:
            logger.warning(f"Unknown bump level {level}")

    if config.get("patch_without_tag") and commit_count > 0 and bump is None:
        bump = "patch"
        logger.debug(f"Changing bump level to patch based on config patch_without_tag")

    if (
        not config.get("major_on_zero")
        and current_version.startswith("0.")
        and bump == "major"
    ):
        bump = "minor"
        logger.debug("Changing bump level to minor based on config major_on_zero")

    return bump


@LoggedFunction(logger)
def generate_changelog(from_version: str, to_version: str = None) -> dict:
    """
    Parse a changelog dictionary for the given version.

    :param from_version: The version before where the changelog starts.
                         The changelog will be generated from the commit after this one.
    :param to_version: The last version included in the changelog.
    :return: A dict with changelog sections and commits
    """
    # Additional sections will be added as new types are encountered
    changes: dict = {"breaking": []}

    parser = current_commit_parser()
    body_process = processors.noop
    for processor in config.get("changelog_body_processors", "").split(","):
        processor = processor.strip()
        if processor:
            body_process |= getattr(processors, processor, None) or import_path(
                processor
            )

    subject_process = (
        processors.noop
        if config.get("changelog_capitalize") is False
        else processors.capitalize
    )
    for processor in config.get("changelog_subject_processors", "").split(","):
        processor = processor.strip()
        if processor:
            subject_process |= getattr(processors, processor, None) or import_path(
                processor
            )

    for commit in get_commits_for_chagelog(from_version, to_version):
        _hash = commit.hexsha

        try:
            message: ParsedCommit = parser(commit.message)
            if message.type not in changes:
                logger.debug(f"Creating new changelog section for {message.type} ")
                changes[message.type] = list()

            # Processing
            subject, body = message.descriptions[0], "\n".join(message.descriptions[1:])
            subject, body = subject_process(subject), body_process(body)
            formatted_message = subject
            if body:
                formatted_message = f"{formatted_message}\n\n{body}"

            # By default, feat(x): description shows up in changelog with the
            # scope bolded, like:
            #
            # * **x**: description
            if config.get("changelog_scope") and message.scope:
                formatted_message = f"**{message.scope}:** {formatted_message}"

            changes[message.type].append((_hash, formatted_message))

            if message.breaking_descriptions:
                # Copy breaking change descriptions into changelog
                for paragraph in message.breaking_descriptions:
                    changes["breaking"].append((_hash, subject_process(paragraph)))
            elif message.bump == 3:
                # Major, but no breaking descriptions, use commit subject instead
                changes["breaking"].append((_hash, subject))

        except UnknownCommitMessageStyleError as err:
            logger.debug(f"Ignoring UnknownCommitMessageStyleError: {err}")

    return changes
