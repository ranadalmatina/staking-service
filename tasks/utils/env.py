import os

# Try environment files in the following order
ENV_FILES = ['tasks/.env', '.env']


def _find_env_var(name, env_file):
    """
    Search all lines from the .env file to find the named env var

    @param name: variable name to read
    @param env_file: env file to read variable from
    """
    with open(env_file) as f:
        lines = f.readlines()

        for line in lines:
            if name in line:
                var_name, value = line.split('=', maxsplit=1)
                assert var_name == name
                return value.strip()


def _read_env_var(name):
    """
    Search all env files for the named environment variable and return its value.

    @param name: variable name to read
    """
    for file in ENV_FILES:
        env_file = os.path.abspath(file)
        assert os.path.exists(env_file)

        value = _find_env_var(name=name, env_file=env_file)
        if value is not None:
            return value


def read_env_var(name):
    """
    Search all env files for the named environment variable and return its value.
    Raises AssertionError if no value is found for the given variable name.

    @param name: variable name to read
    """
    value = _read_env_var(name)
    assert value is not None
    return value
