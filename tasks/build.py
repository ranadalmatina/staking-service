import re
from datetime import datetime

from invoke import task
from invoke.exceptions import Exit

from .utils import get_latest_changelog_version, read_version_file


def verify_changelog(next_version, allow_early_date=False):
    """
    Read the version string from the Changelog and verify the date and
    version match with today's date and the next version we are trying to set.
    """
    version_string = get_latest_changelog_version()
    version_string, date_string = version_string.split('(')
    assert next_version in version_string
    date_str = date_string.split(')')[0]
    release_date = datetime.strptime(date_str, '%d/%m/%y').date()
    if allow_early_date:
        assert release_date <= datetime.now().date()
    else:
        assert release_date == datetime.now().date()


@task
def version(c, part, allow_early=False):
    """
    Bump the version number, but first verify that these match the
    data in the Changelog.
    """
    cmd = f'bumpversion --new-version {part} --allow-dirty'
    result = c.run(f'{cmd} --dry-run --list')
    match = re.search('^new_version=([0-9.]+)$', result.stdout, re.MULTILINE)
    next_version = match.group(1)

    # Ensure that we have used a different version string
    current_version = read_version_file()
    assert current_version != next_version

    result = c.run('grep {} CHANGELOG.md'.format(next_version), warn=True)
    if result.failed:
        raise Exit('Changelog not updated.')

    try:
        verify_changelog(next_version, allow_early_date=allow_early)
    except AssertionError:
        raise
    else:
        c.run(cmd)


@task
def clean(ctx):
    ctx.run("find . -name '*.pyc' -delete")
