#! /usr/bin/env python3

import argparse
import os

from jira import JIRA

JIRA_PROJECT = 'RHODS'
ISSUE_STATUS_FILTER = 'Resolved'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    parser.add_argument('-b', '--release', required=True,
                        help='The specific release to get all the issues from')
    return parser.parse_args()


def main():
    args = parse_args()
    assert os.path.exists(args.token_file)
    with open(args.token_file) as f:
        token = f.read().strip()

    jira = JIRA('https://issues.redhat.com', token_auth=token)
    issues_in_release = jira.search_issues(
        'Project={} AND "Target Release"={} AND Status="{}"'.format(
            JIRA_PROJECT, args.release, ISSUE_STATUS_FILTER))

    for issue in issues_in_release:
        print(issue.key)

if __name__ == '__main__':
    main()
