import errno
import os
import platform
import subprocess


class Client:

    def __init__(self, cli_path=None, config_dir=None, credential=None, credential_passphrase=None):
        """Initialize a new client.

        For now, the client delegates the task to our GoLang Client via the CLI.
        The CLI will be open-sourced soon.

        :param str cli_path: The path of the SecretHub CLI to use. When the cli_path is None a default of
                              "/usr/local/secrethub/secrethub" or "C://Program Files/SecretHub/secrethub.exe" (Windows)
                              is used.
        :param str config_dir: The path to the configuration directory to use. This directory can be used to store the credential in.
        :param str credential: When supplied, this credential will be used to decrypt your accounts encryption key.
        :param str credential_passphrase: The passphrase used to decrypt the credential.
        """
        self._cli_path = '/usr/local/secrethub/secrethub'
        if platform.system() == 'Windows':
            self._cli_path = 'C://Program Files/SecretHub/secrethub.exe'
        if cli_path is not None:
            self._cli_path = cli_path
        self.config_dir = config_dir
        self.credential = credential
        self.credential_passphrase = credential_passphrase

    def read(self, path):
        """Read a secret on the given path.

        :param str path:: The path of the secret to read.
        :raises ReadError when reading fails.
        :raises CLINotFound when the CLI is not found on the configured path.
        :raises CLINotPermitted when the user does not have permission to execute the CLI.
        :return: The value of the read secret.
        :rtype: str
        """
        secret, err = self._run_command(['read', path])
        if err != '':
            raise ReadError(msg=err)
        if secret.endswith('\n'):
            secret = secret[:-1]
        return secret

    def write(self, path, value):
        """Create a new secret version on the given path with the given value.

        :param str path: The path to write the secret to.
        :raises WriteError when writing fails.
        :raises CLINotFound when the CLI is not found on the configured path.
        :raises CLINotPermitted when the user does not have permission to execute the CLI.
        :param str value: The secret value.
        :return: The value that was written.
        :rtype: str
        """
        _, err = self._run_command(['write', path], stdin=value)
        if err != '':
            raise WriteError(msg=err)
        return value

    def generate(self, path, length, symbols):
        """Create a new secret version on the given path with a random value.

        :param str path: The path to write the secret to.
        :param int length: The length of the secret to write.
        :param bool symbols: Whether the random value should contain symbols.
        :raises GenerateError when generating the secret fails.
        :raises ReadError when reading the generated secret fails.
        :raises CLINotFound when the CLI is not found on the configured path.
        :raises CLINotPermitted when the user does not have permission to execute the CLI.
        :return: The value of the written secret.
        :rtype: str
        """
        # Command
        command = ['generate', 'rand']

        # Flags
        if symbols:
            command.append('--symbols')

        # Arguments
        command.append(path)

        if length > 0:
            command.append(str(length))

        # Execute
        res, err = self._run_command(command)
        if err != '':
            raise GenerateError(msg=err)

        return self.read(path)

    def _run_command(self, args, stdin=None):
        """Runs a CLI command.

        :param list(str) args: The arguments of the CLI command (e.g. read /path/to/read)
        :param str stdin: Input to supply on stdin.
        :return: The output on stdout and stderr.
        :rtype: (str, str)
        """
        command = [self._cli_path]
        if self.config_dir:
            command.append('--config-dir={}'.format(self.config_dir))
        command += args

        env = os.environ.copy()
        if self.credential:
            env['SECRETHUB_CREDENTIAL'] = self.credential
        if self.credential_passphrase:
            env['SECRETHUB_CREDENTIAL_PASSPHRASE'] = self.credential_passphrase

        try:
            if stdin:
                p = subprocess.Popen(
                    command,
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )
            else:
                p = subprocess.Popen(
                    command,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise CLINotFound(self._cli_path)
            if e.errno == errno.EACCES:
                raise CLINotPermitted(self._cli_path)
            raise
        return p.communicate(input=stdin)


class Error(Exception):
    """Base class for SecretHub client exceptions.
    """
    pass


class CLIInaccessible(Error):
    """Base class for SecretHub exceptions caused by an inaccessible CLI.
    """
    pass


class CLINotFound(CLIInaccessible):
    """Error that is raised when the CLI is not found at the configured path.
    """
    def __init__(self, cli_path):
        self.cli_path = cli_path

    def __str__(self):
        return 'cannot find the SecretHub CLI at: {}'.format(self.cli_path)


class CLINotPermitted(CLIInaccessible):
    """Error that is raised when the user has no execute permissions on the CLI.

    The user that runs the python process is the user that should have the permission.
    """
    def __init__(self, cli_path):
        self.cli_path = cli_path

    def __str__(self):
        return 'cannot access the SecretHub CLI at: {} : permission denied'.format(self.cli_path)


class ReadError(Error):
    """Error that is raised when reading a secret.

    For now, this error is not subclassed, as we are not parsing the CLI's error message.
    When refactoring the client to have its own implementation of read instead of depending
    on the CLI for the implementation, we will subclass this exception with more specific ones.
    For now, you can inspect the message stored in the exception to distinguish between different
    types of read errors.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class WriteError(Error):
    """Error that is raised when writing a secret.

    For now, this error is not subclassed, as we are not parsing the CLI's error message.
    When refactoring the client to have its own implementation of write instead of depending
    on the CLI for the implementation, we will subclass this exception with more specific ones.
    For now, you can inspect the message stored in the exception to distinguish between different
    types of write errors.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class GenerateError(Error):
    """Error that is raised when generating a secret.

    For now, this error is not subclassed, as we are not parsing the CLI's error message.
    When refactoring the client to have its own implementation of generate instead of depending
    on the CLI for the implementation, we will subclass this exception with more specific ones.
    For now, you can inspect the message stored in the exception to distinguish between different
    types of generate errors.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
