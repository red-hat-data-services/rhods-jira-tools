#! /usr/bin/env python3

import argparse
import os

from jira import JIRA


CDW_RELEASE_FIELD = 'customfield_12311241'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--issue', required=True, action='append',
                        dest='issues',
                        help='The JIRA issue to check e.g. "RHODS-2001"')
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    return parser.parse_args()


def main():
    args = parse_args()
    assert os.path.exists(args.token_file)
    with open(args.token_file) as f:
        token = f.read().strip()

    jira = JIRA('https://issues.redhat.com', token_auth=token)
    issues_to_move = sorted(set(args.issues))
    for issue_key in issues_to_move:
        issue = jira.issue(issue_key)

        fully_acked = issue.raw['fields'][CDW_RELEASE_FIELD] == '+'
        if fully_acked:
            print(f'Issue "{issue_key}" is fully acked')
        else:
            print(f'Issue "{issue_key}" is NOT fully acked')


if __name__ == '__main__':
    main()
