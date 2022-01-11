#! /usr/bin/env python3

import argparse
import os

from jira import JIRA


QA_HANDOVER_TRANSITION_ID = '791'
FIXED_IN_BUILD_FIELD = 'customfield_12318450'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--issue', required=True, action='append',
                        dest='issues',
                        help='The JIRA issue to be transitioned e.g. "RHODS-2001"')
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    parser.add_argument('-f', '--fix-version', required=True,
                        help='The version that the issue was addressed in')
    parser.add_argument('-b', '--build', required=True,
                        help='The specific build that the issue was addressed in')
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

        current_status = issue.fields.status
        if str(current_status) != 'Resolved':
            print((f'Issue {issue_key} is not currently in the "Resolved" '
                   'state. Please progress it to resolved before attempting '
                   'to progress it to "Ready for QA".'))
            continue
        available_transitions = [t['id'] for t in jira.transitions(issue)]
        if QA_HANDOVER_TRANSITION_ID not in available_transitions:
            print('This issue cannot be transitioned to the "Ready for QA" state.')
            continue

        transition_fields = {
            'fixVersions': [{'name': args.fix_version}],
            FIXED_IN_BUILD_FIELD: args.build
        }
        jira.transition_issue(issue, QA_HANDOVER_TRANSITION_ID,
                              fields=transition_fields)
        print(f'{issue_key} successfully handed over to QE.')


if __name__ == '__main__':
    main()
