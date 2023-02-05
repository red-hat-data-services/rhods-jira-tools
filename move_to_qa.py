#! /usr/bin/env python3

import argparse
import os
import time

from jira import JIRA

QA_HANDOVER_TRANSITION_ID = "791"
FIXED_IN_BUILD_FIELD = "customfield_12318450"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--issue",
        required=True,
        action="append",
        dest="issues",
        help='JIRA issue to be transitioned e.g. "RHODS-2001"',
    )
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
        help="The target release that the issue was addressed in",
    )
    parser.add_argument(
        "-b",
        "--build",
        required=True,
        help="The specific build version that the issue was addressed in",
    )
    return parser.parse_args()


def main():
    """
    Handle transitioning a given Jira issue to the "Ready for QA" state.
    """
    args = parse_args()
    assert os.path.exists(args.token_file)
    with open(args.token_file) as f:
        token = f.read().strip()

    jira = JIRA("https://issues.redhat.com", token_auth=token)
    issues_to_move = sorted(set(args.issues))
    for issue_key in issues_to_move:
        issue = jira.issue(issue_key)

        # pre-check JIRA issue status
        current_status = issue.fields.status
        if str(current_status) == "Ready for QA":
            print(
                (
                    f'Issue {issue_key} is already in the "Ready for QA" '
                    "state. Skipping."
                )
            )
            continue
        if str(current_status) != "Resolved":
            print(
                (
                    f'Issue {issue_key} is not currently in the "Resolved" '
                    'state. Please progress it to "Resolved" before attempting '
                    'to progress it to "Ready for QA".'
                )
            )
            continue

        applicable_transitions = [t["id"] for t in jira.transitions(issue)]
        if QA_HANDOVER_TRANSITION_ID not in applicable_transitions:
            print(f'{issue_key} cannot be transitioned to the "Ready for QA" state.')
            continue

        # perform transition
        transition_fields = {
            "fixVersions": [{"name": args.fix_version}],
            FIXED_IN_BUILD_FIELD: args.build,
        }
        jira.transition_issue(
            issue, QA_HANDOVER_TRANSITION_ID, fields=transition_fields
        )

        # post-check
        time.sleep(1)
        if str(jira.issue(issue_key).fields.status) == "Ready for QA":
            print(f'{issue_key} successfully set to "Ready for QA".')


if __name__ == "__main__":
    main()
