# SPDX-FileCopyrightText: 2022 Alec Delaney, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
from typing import Literal
from typer import Typer
from github.Repository import Repository
from github import GithubException
from library_functions import StrPath
from iterate_libraries import RemoteLibFunc_IterResult, iter_local_bundle_with_func, iter_remote_bundle_with_func


app = Typer()


def check_ci(
    lib_repo: Repository,
    contents: str,
    filepath: str,
) -> bool:
    """Checks whether the contents of the file are the same."""
    print(f"Checking {lib_repo.name}")
    try:
        file_contents = lib_repo.get_contents(filepath)
        decoded = file_contents.decoded_content.decode("utf-8")
        return decoded == contents
    except GithubException:
        return False


def is_archived(lib_repo: Repository) -> bool:
    """Checks whether a repository is archived."""
    print(f"Checking {lib_repo.name}")
    return lib_repo.archived


def check_cis(gh_token: str, contents: str, file: str) -> list[RemoteLibFunc_IterResult[bool]]:
    """Checks the contents across all the libraries."""
    return iter_remote_bundle_with_func(gh_token, [(check_ci, (contents, file), {})])


def are_archived(gh_token: str) -> list[RemoteLibFunc_IterResult]:
    """Checks which repositories are archived."""
    return iter_remote_bundle_with_func(gh_token, [(is_archived, (), {})])


@app.command()
def check_similarity(gh_token: str, compare_file: str, search_filepath: str) -> None:
    """Compares contents of file with that of a repository's file."""
    print("Running...")

    with open(compare_file, encoding="utf-8") as compfile:
        contents = compfile.read()

    results = check_cis(gh_token, contents, search_filepath)

    fail_list = [repo_name.name for repo_name, repo_results in results if not repo_results[0]]
    for fail in fail_list:
        print(f"Failed: {fail}")


@app.command()
def check_archived(gh_token: str) -> None:
    """Gets which repositories are archived."""
    print("Running...")
    results = are_archived(gh_token)
    archived = [repo_name.name for repo_name, repo_results in results if repo_results[0]]
    for repo in archived:
        print(f"Archvied: {repo}")


def delete_ci_file(lib_path: StrPath, filepath: str) -> bool:
    """Delete the specified file in the repository."""
    full_filepath = os.path.join(lib_path, filepath)
    try:
        os.remove(full_filepath)
        return True
    except FileNotFoundError:
        return False


def add_ci_file(lib_path: StrPath, filepath: str, contents: str) -> Literal[True]:
    """Add the specified file with contents to the repository."""
    full_filepath = os.path.join(lib_path, filepath)
    with open(full_filepath, mode="w", encoding="utf-8") as newfile:
        newfile.write(contents)
    return True
    

@app.command()
def rework_ci_files(lib_path: str):
    """Rework all the CI files in the bundle"""
    with open("build_final.yml", encoding="utf-8") as buildfile:
        build_contents = buildfile.read()
    with open("build_final.yml", encoding="utf-8") as ghfile:
        gh_contents = ghfile.read()
    with open("build_final.yml", encoding="utf-8") as pypifile:
        pypi_contents = pypifile.read()

    results = iter_local_bundle_with_func(
        lib_path,
        [
            (
                delete_ci_file, (".github/workflows/build.yml",), {}
            ),
            (
                delete_ci_file, (".github/workflows/release.yml",), {}
            ),
            (
                add_ci_file, (".github/workflows/build.yml", build_contents), {}
            ),
            (
                add_ci_file, (".github/workflows/release_gh.yml", gh_contents), {}
            ),
            (
                add_ci_file, (".github/workflows/release_pypi.yml", pypi_contents), {}
            ),
        ],
    )

    fail_list = [repo_name for repo_name, repo_results in results if not all(repo_results)]
    for failed in fail_list:
        print(f"Failed: {failed}")

app()
