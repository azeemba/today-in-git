from dataclasses import dataclass
import subprocess
import json

from datetime import datetime

from functools import reduce

@dataclass
class Commit:
    sha: str
    message: str
    timestamp: datetime
    def __str__(self) -> str:
        return f"{self.timestamp: }\n{self.message}"

@dataclass
class Repo:
    name: str
    description: str
    created: datetime
    commits: list[Commit]
    def __str__(self) -> str:
        return f"{self.name}, {self.description},{self.created}\n{self.commits}"


def parse_iso_generous(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%Sz")

def gh_api(path, paginate=False, method="GET", **kwargs):
    cmd = ["gh", "api", path, "--method", method]
    if paginate:
        cmd += ["--paginate", "--slurp"]

    for key, value in kwargs.items():
        cmd += ["--field", f"{key}={value}"]

    cmd += ["--cache", "20h"]
    # print(" ".join(cmd))
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


def get_main_repos() -> list[Repo]:
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
                        createdAt
                        parent {
                            nameWithOwner
                            description
                            createdAt
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

    main_repos: list[Repo] = []
    for page in repos_json:
        nodes = page["data"]["viewer"]["repositories"]["nodes"]
        for item in nodes:
            root = item
            if item["isFork"]:
                root = item["parent"]

            created = parse_iso_generous(root["createdAt"])
            main_repos.append(Repo(root["nameWithOwner"], root["description"], created, []))

    return main_repos


def get_commits(repo: str, author: str, since: datetime, until: datetime) -> list[Commit]:
    """
    gh api /repos/azeemba/azeemba.com/commits --method GET --field author="azeemba" --field per_page=1 --cache 1h
    """

    def make_iso(d: datetime):
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")

    commits_json = gh_api(
        f"/repos/{repo}/commits",
        paginate=True,
        author=author,
        since=make_iso(since),
        until=make_iso(until),
    )

    def makeLightCommit(commit):
        return Commit(
            commit["sha"],
            commit["commit"]["message"],
            parse_iso_generous(commit["commit"]["author"]["date"]))

    commits = [makeLightCommit(c) for c in commits_json]
    return commits

