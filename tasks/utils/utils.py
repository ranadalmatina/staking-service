import os


def read_change_log():
    """
    Read the first four lines of the change log.
    """
    change = os.path.abspath('CHANGELOG.MD')
    assert os.path.exists(change)

    lines = []
    with open(change) as f:
        for _ in range(4):
            line = f.readline().strip()
            if line:
                lines.append(line)
    return lines


def read_version_file():
    """
    Read the current version out of the version file.
    """
    version = os.path.abspath('VERSION')
    assert os.path.exists(version)

    with open(version) as f:
        return f.readline().strip()


def get_latest_changelog_version():
    """
    Read the most recent version line of the change log.
    """
    lines = read_change_log()
    assert len(lines) == 2
    assert '# Change Log' in lines[0]
    return lines[1]
