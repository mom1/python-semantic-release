class Commit:
    hexsha: str
    summary: str
    message: str

    def __init__(self, hexsha: str, message: str):
        self.hexsha = hexsha
        self.message = message
        self.summary = message.split('\n\n')[0]

    def __getitem__(self, index):
        return (self.hexsha, self.message)[index]


MAJOR = Commit(
    "221",
    "feat(x): Add super-feature\n\n"
    "BREAKING CHANGE: Uses super-feature as default instead of dull-feature.",
)
MAJOR2 = Commit(
    "222",
    "feat(x): Add super-feature\n\nSome explanation\n\n"
    "BREAKING CHANGE: Uses super-feature as default instead of dull-feature.",
)
MAJOR_MENTIONING_1_0_0 = Commit(
    "223",
    "feat(x): Add super-feature\n\nSome explanation\n\n"
    "BREAKING CHANGE: Uses super-feature as default instead of dull-feature from v1.0.0.",
)
MAJOR_MULTIPLE_FOOTERS = Commit(
    "244",
    "feat(x): Lots of breaking changes\n\n"
    "BREAKING CHANGE: Breaking change 1\n\n"
    "Not a BREAKING CHANGE\n\n"
    "BREAKING CHANGE: Breaking change 2",
)
MAJOR_EXCL_WITH_FOOTER = Commit(
    "231",
    "feat(x)!: Add another feature\n\n"
    "BREAKING CHANGE: Another feature, another breaking change",
)
MAJOR_EXCL_NOT_FOOTER = Commit(
    "232",
    "fix!: Fix a big bug that everyone exploited\n\nThis is the reason you should not exploit bugs",
)
MINOR = Commit("111", "feat(x): Add non-breaking super-feature")
PATCH = Commit("24", "fix(x): Fix bug in super-feature")
NO_TAG = Commit("191", "docs(x): Add documentation for super-feature")
UNKNOWN_STYLE = Commit("7", "random commits are the worst")

ALL_KINDS_OF_COMMIT_MESSAGES = [MINOR, MAJOR, MINOR, PATCH]
MINOR_AND_PATCH_COMMIT_MESSAGES = [MINOR, PATCH]
PATCH_COMMIT_MESSAGES = [PATCH, PATCH]
MAJOR_LAST_RELEASE_MINOR_AFTER = [MINOR, Commit("22", "1.1.0"), MAJOR]
MAJOR_MENTIONING_LAST_VERSION = [MAJOR_MENTIONING_1_0_0, Commit("22", "1.0.0"), MAJOR]
