from collections import defaultdict

from ..settings import config

try:
    from .processing import get_handler
except ImportError:
    get_handler = lambda x, y: lambda z: z


def changelog_grouping(
    owner: str, repo_name: str, changelog: list, changelog_sections: list, **kwargs
):
    """Grouping commits by fild.

    It will work only with `commit_analyzer=semantic_release.history.logs.get_commits`
    """
    grouping_field = config.get("grouping_field", "type").strip()
    sections = defaultdict(list)
    handler = get_handler("changelog_section_handlers")
    for commit in changelog[:]:
        changelog.pop()
        sections[commit[grouping_field]].append(commit)

    changelog.extend(
        [
            {"section": handler(section), "commits_section": sections[section]}
            for section in changelog_sections
            if section and sections[section]
        ]
    )
