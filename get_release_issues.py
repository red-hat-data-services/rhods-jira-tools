#! /usr/bin/env python3

import argparse
import os

from jira import JIRA


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--token-file",
        required=True,
        help="Path to a local file containing the JIRA personal access token",
    )
    parser.add_argument(
        "-r",
        "--release",
        required=True,
        help="The specific release to get all the issues from",
    )
    parser.add_argument(
        "-p",
        "--project",
        required=False,
        default="RHODS",
        help="The specific JIRA project to query issues from",
    )
    parser.add_argument(
        "-s",
        "--status",
        required=False,
        default="Resolved",
        help="The specific issue status to query issues from",
    )
    return parser.parse_args()


def main():
    """
    Return all the issues in match query by project, status and release.
    By default, it sets to use "RHODS" project with issues status in "Resolved"
    """
    args = parse_args()
    assert os.path.exists(args.token_file)
    with open(args.token_file) as f:
        token = f.read().strip()

    jira = JIRA("https://issues.redhat.com", token_auth=token)
    issues_in_release = jira.search_issues(
        'Project={} AND "Target Release"={} AND Status="{}"'.format(
            args.project, args.release, args.status
        )
    )

    for issue in issues_in_release:
        print(issue.key)


if __name__ == "__main__":
    main()
