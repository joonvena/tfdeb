import logging
import os
from typing import Dict, List
from urllib.parse import urlparse

import gitlab
import hcl
import requests
from github import Github
from github.Repository import Repository
from gitlab.base import RESTObject
from gitlab.v4.objects import ProjectMergeRequest

from utils import parse_versions

TF_REGISTRY_BASE_URL = "https://registry.terraform.io/v1"
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_PROJECT = os.getenv("GITLAB_PROJECT", "")
BRANCH = os.getenv("BRANCH", "master")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
TF_VERSIONS_FILE_PATH = os.getenv("TF_VERSIONS_FILE_PATH", "versions.tf")


LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def parse_hcl() -> Dict:
    """Convert file from HCL to Dictionary for parsing"""
    with open("/tmp/versions.tf", "r", encoding="utf-8") as versions_file:
        return hcl.load(versions_file)["terraform"]


def is_latest_version(current_version: str, latest_version: str) -> bool:
    """Check if current version is latest available version"""
    return current_version == latest_version


def get_all_versions_between_current_and_latest(
    all_versions: List[str], current_version: str
) -> List[str]:
    """
    Find all versions between the current and
    latest and store them in a list
    """
    versions = []
    current_version_index = all_versions.index(current_version) + 1
    for version in all_versions[current_version_index:]:
        versions.append(version)
    return versions


def update_merge_request_branch_exists(
    gitlab_project: RESTObject, merge_request_branch: str
) -> bool:
    """Check if Provider update mr already exists"""
    if gitlab_project.branches.get(merge_request_branch):
        return True
    return False


def get_provider_repository(g: Github, source: str) -> Repository:
    """Get provider repository information"""
    parts = urlparse(source)
    owner, repository_name = parts.path.strip("/").split("/")
    return g.get_repo(f"{owner}/{repository_name}")


def create_branch(
    gitlab_project: RESTObject,
    merge_request_branch: str,
    commit_message: str,
    updated_version: str,
) -> RESTObject:
    """
    Create branch for provider update and
    update the provider version file
    """
    commit_data = {
        "branch": merge_request_branch,
        "start_branch": BRANCH,
        "commit_message": commit_message,
        "actions": [
            {
                "action": "update",
                "file_path": {TF_VERSIONS_FILE_PATH},
                "content": updated_version,
            }
        ],
    }
    return gitlab_project.commits.create(commit_data)


def create_merge_request(
    gitlab_project: RESTObject,
    merge_request_branch: str,
    commit_message: str,
    release_notes: str,
) -> RESTObject:
    """
    Create merge request from the branch
    created by create_branch function
    """
    merge_request_data = {
        "source_branch": merge_request_branch,
        "target_branch": BRANCH,
        "title": commit_message,
        "labels": "dependencies,terraform",
        "description": release_notes,
    }
    return gitlab_project.mergerequests.create(merge_request_data)


def check_for_obsolete_merge_request(
    gitlab_project: RESTObject,
    merge_request_branch: str,
) -> List[ProjectMergeRequest]:
    """
    Check if merge request is obsolete eg.
    provider was updated manually
    """
    return gitlab_project.mergerequests.list(
        state="opened",
        source_branch=merge_request_branch,
        labels=["dependencies, terraform"],
    )


def close_obsolete_merge_request(
    gitlab_project: RESTObject,
    merge_request_id: str,
) -> None:
    """
    Closes obsolete merge request
    """
    gitlab_project.mergerequests.delete(merge_request_id)


def delete_obsolete_merge_request_branch(
    gitlab_project: RESTObject,
    branch: str,
) -> None:
    """
    Deletes the source branch of closed obsolete merge request
    """
    gitlab_project.branches.delete(branch)


def main():
    gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN, user_agent="tfdeb/0.1")

    g = Github(GITHUB_TOKEN)

    gitlab_project = gl.projects.get(GITLAB_PROJECT)

    with open("/tmp/versions.tf", "wb") as versions_file:
        gitlab_project.files.raw(
            file_path=TF_VERSIONS_FILE_PATH,
            ref=BRANCH,
            streamed=True,
            action=versions_file.write,
        )

    providers = parse_hcl()

    for provider in providers["required_providers"]:
        provider_source = providers["required_providers"][provider]["source"]
        current_version = providers["required_providers"][provider]["version"]

        provider_details = requests.get(
            f"{TF_REGISTRY_BASE_URL}/providers/{provider_source}"
        ).json()
        latest_version = provider_details["version"]
        source = provider_details["source"]
        all_versions = provider_details["versions"]
        merge_request_branch = f"tfdep/{provider_source}--{latest_version}"
        commit_message = (
            f"Bump {provider_source} from version {current_version} > {latest_version}"
        )

        if not is_latest_version(current_version, latest_version):
            if update_merge_request_branch_exists(gitlab_project, merge_request_branch):
                LOG.info(
                    "Skipping update as merge request branch exists with name %s",
                    merge_request_branch,
                )
                continue
            LOG.info(
                "Provider %s is not up to date. Updating version from %s to %s",
                provider,
                current_version,
                latest_version,
            )

            with open("/tmp/versions.tf", "r", encoding="utf-8") as versions_file:
                versions_tf = versions_file.read()
                updated_version = parse_versions(
                    versions_tf, provider_source, current_version, latest_version
                )

                create_branch(
                    gitlab_project,
                    merge_request_branch,
                    commit_message,
                    updated_version,
                )

                create_merge_request(
                    gitlab_project, merge_request_branch, commit_message, ""
                )

        LOG.info(
            "Latest version running for provider %s. Checking for obsolete merge requests.",
            provider,
        )
        obsolete_merge_request = check_for_obsolete_merge_request(
            gitlab_project, merge_request_branch
        )

        if obsolete_merge_request:
            LOG.info(
                "Found merge request with id %s that is obsolete. Closing merge request.",
                obsolete_merge_request[0].iid,
            )
            close_obsolete_merge_request(gitlab_project, obsolete_merge_request[0].iid)
            delete_obsolete_merge_request_branch(
                obsolete_merge_request[0].source_branch
            )


if __name__ == "__main__":
    main()
