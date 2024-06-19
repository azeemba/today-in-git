import argparse
from datetime import timedelta, timezone, datetime, time
from github_helper import get_user, get_main_repos, get_commits


def main(args):
    user = get_user()
    print(f"Will act as {user}")

    repos = get_main_repos()
    now = datetime.now(timezone.utc)

    for repo in repos:
        start_of_day: datetime = datetime.combine(now.date(), time.min) - timedelta(
            days=args.days - 1
        )
        end_of_day: datetime = datetime.combine(now.date(), time.max) - timedelta(
            seconds=1
        )

        # Adjust
        def move_back_a_year():
            nonlocal start_of_day
            nonlocal end_of_day
            start_of_day = start_of_day.replace(year=start_of_day.year - 1)
            end_of_day = end_of_day.replace(year=end_of_day.year - 1)

        move_back_a_year()

        max_iters = 50
        count = 0

        print(f"Checking {repo.name}, going back to {repo.created.year}.")
        while end_of_day > repo.created and count < max_iters:
            count += 1
            commits = get_commits(repo.name, user, start_of_day, end_of_day)
            repo.commits.extend(commits)

            move_back_a_year()

    repos_with_results = [r for r in repos if r.commits]

    print("----------------------\n")
    for repo in repos_with_results:
        print(f"Repo: {repo.name}")
        for i in range(len(repo.commits)):
            commit = repo.commits[i]
            print(str(commit))
            if i + 1 < len(repo.commits):
                print("--")
        print("----------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch commits from today in past years"
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days to look back (default: 7)"
    )
    args = parser.parse_args()

    main(args)
