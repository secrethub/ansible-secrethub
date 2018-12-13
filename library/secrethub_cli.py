import errno
import os
import platform
import shutil
import subprocess
import tempfile
import zipfile

from ansible.module_utils.secrethub_base import BaseModule

DOCUMENTATION = '''
---
module: secrethub_cli

short_description: Install the SecretHub CLI

version_added: "2.6"

description:
    - "Installs the SecretHub CLI"

options:
  install_dir:
    description:
        The path where the CLI is installed. This defaults to `/usr/local/secrethub/` on Unix systems
        and `C://Program Files/SecretHub/` on Windows.
    required: false
  state:
    description:
        The state present implies that the CLI should be installed if necessary.
        Absent implies that the CLI should be uninstalled if present.
    choices: ['present', 'absent']
    default: 'present'
    required: false
  version:
    description:
        The version of the CLI that should be installed.
        When state is absent, version will be ignored.
    default: 'latest'
    required: false

author:
    - Simon Barendse (@simonbarendse)
    - Marc Mackenbach (@mackenbach)
'''

EXAMPLES = '''
# Default
- name: Ensure the SecretHub CLI is installed
  secrethub_cli:

# Specific version
- name: Ensure version 1.0.0 of the SecretHub CLI is installed
  screthub_cli:
    version: 1.0.0

# Uninstall
- name: Ensure the SecretHub CLI is not installed
  secrethub_cli:
    state: absent

# Install at custom location
- name: Ensure the SecretHub CLI is installed
  secrethub_cli:
    install_dir: /opt/

'''

RETURN = '''
version:
  description: The currently installed version of the SecretHub CLI.
  type: str
bin_path:
  description: The absolute path to the location of the installed binary.
  type: str
install_dir:
  description: The absolute path to the directory in which the secrethub binary is installed.
               Add this directory to the PATH to make the CLI globally accessible.
'''


class CLIModule(BaseModule):

    def __init__(self):
        argument_spec = {
            'install_dir': {
                'required': False,
                'type': "str",
            },
            'state': {
                'required': False,
                'type': "str",
                'choices': ['present', 'absent'],
                'default': 'present',
            },
            'version': {
                'required': False,
                'type': "str",
                'default': 'latest',
            },
        }
        super(CLIModule, self).__init__(argument_spec)

    def run(self):
        """ Installs or upgrades the SecretHub CLI when needed.

        Installs the SecretHub CLI when the CLI is not yet installed in the configured path.
        When a different version of the CLI is installed, it is upgraded/downgraded.

        When the module successfully exists, it returns the currently installed version and
        the bin_path and install_dir in which the CLI is installed.
        """
        current_version = self.current_version()

        self.returns.update({
            'bin_path': self.bin_path(),
            'install_dir': self.install_dir(),
            'version': current_version,
        })
        if self.params.get('state', 'present') == 'present':
            target_version = self.target_version()
            if current_version != target_version:
                self.install(version=target_version)
        if self.params.get('state', 'present') == 'absent':
            if current_version is not None:
                self.uninstall()
        self.exit()

    def current_version(self):
        """ Get the current version of the SecretHub CLI.

        Returns the current version of the SecretHub CLI installed in the configured
        path. When the SecretHub CLI is not installed in the configured path, None
        is returned. When the SecretHub CLI is installed in the configured path,
        but the user that runs the module has no permission to execute it, the
        module fails.

        :return: The current version of the SecretHub CLI, or None
                      if the SecretHub CLI is not installed in the configured path.
        :rtype: str
        """
        path = self.bin_path()
        try:
            p = subprocess.Popen(
                [self.bin_path(), '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            version, err = p.communicate()
            # TODO SHDEV-1098: Why does the CLI return the version on stderr?
            # Remove newline
            return err[:-1].decode()
        except OSError as e:
            if e.errno == errno.EACCES:
                self.fail('secrethub_cli: found {} but cannot execute: {}'.format(path, e))
            if e.errno == errno.ENOENT:
                # The file does not exist, so there is no current version.
                return None
            raise

    def target_version(self):
        """
        By default the latest version of the CLI is installed. This
        can be overridden by the user by setting the "version"
        parameter of the module.

        :return: The target version of the SecretHub CLI.
        :rtype: str
        """
        target_version = self.params.get('version', 'latest')
        if target_version == 'latest':
            target_version = self.latest_version()
        return target_version

    def latest_version(self):
        """ Fetches the latest SecretHub CLI version from the SecretHub server.

        :return: The latest SecretHub CLI version.
        :rtype: str
        """
        try:
            # Python 3
            from urllib.request import urlopen
        except ImportError:
            # Python 2
            from urllib2 import urlopen

        try:
            return urlopen('https://get.secrethub.io/releases/LATEST').read().decode()
        except IOError as e:
            self.fail('secrethub_cli: failed to fetch latest version: {}'.format(e))

    def bin_path(self):
        """
        :return: The absolute path to the cli binary.
        :rtype: str
        """
        bin_name = 'secrethub'
        if platform.system() == 'Windows':
            bin_name = 'secrethub.exe'
        return os.path.join(self.install_dir(), bin_name)

    def install_dir(self):
        """ Get the installation directory for the CLI.

        The first of the following is returned:
        1. The value of the cli_path parameter in the playbook.
        2. C://Program Files/SecretHub/ (on Windows)
        3. /usr/local/secrethub/

        :return: The directory in which the binary should be installed.
        :rtype: str
        """
        path = self.params.get('install_dir')
        if path:
            return path
        if platform.system() == 'Windows':
            # TODO: Test whether this works on a windows machine.
            return 'C://Program Files/SecretHub/'
        return '/usr/local/secrethub/'

    def fetch_binary(self, version):
        """ Fetches the SecretHub CLI binary to a temporary file.

        The SecretHub CLI binary for this system and architecture is fetched
        from the SecretHub server and placed in a temporary file.

        :param version: The SecretHub CLI version to fetch.
        :return: The path to the temporary file of the fetched zip
                              and a function to cleanup the temporary files.
        :rtype: (str, lambda)
        """
        fetch_url = 'https://get.secrethub.io/releases/{}/secrethub-{}-{}-{}.zip'.format(
            version,
            version,
            str(platform.system()).lower(),
            'amd64' if str(platform.architecture()[0]).lower() == '64bit' else 'x86'
        )
        tmp_dir = tempfile.mkdtemp()

        def cleanup():
            shutil.rmtree(tmp_dir)

        tmp_file = os.path.join(tmp_dir, 'secrethub-cli.zip')

        try:
            # Python 3
            from urllib.request import urlretrieve
        except ImportError:
            # Python 2
            from urllib import urlretrieve

        try:
            urlretrieve(fetch_url, tmp_file)
        except (IOError, OSError) as e:
            cleanup()
            if e.errno == errno.EACCES:
                # TODO: Do we want to have a more descriptive error message?
                self.fail(msg='secrethub_cli: {}'.format(e))
            raise
        return tmp_file, cleanup

    def install(self, version):
        """ Installs the given version of the SecretHub CLI.

        The CLI is installed in the directory as returned by install_dir.

        :param version: The version of the SecretHub CLI to install.
        """
        tmp_file, cleanup = self.fetch_binary(version)
        try:
            with zipfile.ZipFile(tmp_file, 'r') as cli_zip:
                cli_zip.extractall(path=self.install_dir())
        except (IOError, OSError) as e:
            cleanup()
            if e.errno == errno.EACCES:
                # TODO: Do we want to have a more descriptive error message?
                self.fail('secrethub_cli: {}'.format(e))
            raise
        cleanup()
        os.chmod(self.bin_path(), 0o711)
        self.returns.update({
            'changed': True,
            'version': self.current_version(),
        })

    def uninstall(self):
        """ Removes the binary on the configured path.
        """
        try:
            os.remove(self.bin_path())
            self.returns.update({
                'changed': True,
                'version': self.current_version(),
            })
        except OSError as e:
            if e.errno == errno.EACCES:
                self.fail('secrethub_cli: {}'.format(e))
            raise


def main():
    CLIModule().run()


if __name__ == '__main__':
    main()
