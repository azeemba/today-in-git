# Today In Git

Highlight git contributions you made on this date in previous years!

## How it works

- Uses GitHub API to enumerate your repos
- For forks, it finds the parent repo
- For each repo, it finds commits you made in previous years around this date

## Requirements

- [`gh` cli](https://cli.github.com/)
- Python (no other libraries are needed)

## How to run?

```sh
python main.py
```

Expected result (after a few minutes!):

```log
Will act as azeemba
Checking azeemba/test1, going back to 2013.
Checking git/git, going back to 2010.
Checking azeemba/example going back to 2018.
------------------
Repo: azeemba/test1
2020-06-19: Great commit! Really shook things up
    URL: ...
2020-06-19: Another commit. Not as exciting
    URL: ...
-------------------
```
