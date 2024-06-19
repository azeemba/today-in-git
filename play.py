
from datetime import datetime, timedelta, timezone

from github_helper import get_user, get_main_repos, get_commits

user = get_user()
print(user)
# print(get_repos())
repos = get_main_repos()
print(repos)


commits = get_commits(
    "azeemba/azeemba.com/commits",
    user,
    since=datetime.now(tz=timezone.utc) - timedelta(days=30),
    until=datetime.now(timezone.utc),
)
print(commits)

for c in commits:
    print(c["message"])
