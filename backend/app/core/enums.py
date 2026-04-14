from enum import Enum

class GroupMemberRole(str, Enum):
    LEADER = "leader"
    MEMBER = "member"
    VIEWER = "viewer"


class RecordType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class RecordScope(str, Enum):
    PERSONAL = "personal"
    GROUP = "group"
