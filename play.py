import subprocess
import json

from datetime import datetime, timedelta, timezone

from functools import reduce


def gh_api(path, paginate=False, method="GET", **kwargs):
    cmd = ["gh", "api", path, "--method", method]
    if paginate:
        cmd += ["--paginate", "--slurp"]

    for key, value in kwargs.items():
        cmd += ["--field", f"{key}={value}"]

    cmd += ["--cache", "20h"]
    print(" ".join(cmd))
    output = subprocess.check_output(cmd, text=True)

    parsed = json.loads(output)
    if parsed and paginate and path != "graphql":
        # merge lists
        return reduce(lambda x, y: x + y, parsed, [])
    else:
        return parsed


def get_user():
    user_json = gh_api("/user")
    return user_json["login"]


def get_repos():
    """Get user's repos."""
    repos_json = gh_api("/user/repos", paginate=True)
    repos = [r["full_name"] for r in repos_json]
    return repos


def get_main_repos():
    """
    Get user's repos but for forks fetch the parent repo.
    """
    repos_json = gh_api(
        "graphql",
        paginate=True,
        method="POST",
        query="""
        query($endCursor: String) {
            viewer {
                repositories(first: 100, after: $endCursor) {
                    nodes { 
                        nameWithOwner
                        description
                        isFork
                        parent {
                            nameWithOwner
                            description
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """,
    )

    main_repos = []
    for page in repos_json:
        nodes = page["data"]["viewer"]["repositories"]["nodes"]
        for item in nodes:
            root = item
            if item["isFork"]:
                root = item["parent"]

            main_repos.append(
                {"name": root["nameWithOwner"], "description": root["description"]}
            )

    return main_repos


def get_commits(repo: str, author: str, since: datetime, until: datetime):
    """
    gh api /repos/azeemba/azeemba.com/commits --method GET --field author="azeemba" --field per_page=1 --cache 1h
    """

    def make_iso(d: datetime):
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")

    commits_json = gh_api(
        f"/repos/{repo}",
        paginate=True,
        author=author,
        since=make_iso(since),
        until=make_iso(until),
    )

    def makeLightCommit(commit):
        result = {
            "sha": commit["sha"],
            "message": commit["commit"]["message"],
            "timestamp": commit["commit"]["author"]["date"],
        }
        return result

    commits = [makeLightCommit(c) for c in commits_json]
    return commits


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
