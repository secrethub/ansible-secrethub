import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.client import Client


class BaseModule(AnsibleModule):

    def __init__(self, argument_spec):
        """ Initialize a new SecretHub module.

        This class can be extended to create an Ansible module that uses
        a SecretHub client.

        :param dict argument_spec: Extra arguments to add to the module.
        """
        self.returns = {
            'changed': False,
        }

        argument_spec.update(
            {
                'cli_path': {
                    'required': False,
                    'type': "str",
                },
                'config_dir': {
                    'required': False,
                    'type': "str",
                },
                'credential': {
                    'required': False,
                    'type': "str",
                    'no_log': True,
                },
                'credential_passphrase': {
                    'required': False,
                    'type': "str",
                    'no_log': True,
                },
            }
        )
        super(BaseModule, self).__init__(argument_spec)

    def fail(self, msg):
        """ Fail the module.

        The module returns everything (in the playbook) that is in self.returns.

        :param str msg: The error message to exit the module with.
        """
        self.fail_json(msg=msg, **self.returns)

    def exit(self):
        """ Exit the module.

        The module returns everything (in the playbook) that is in self.returns.
        """
        self.exit_json(**self.returns)

    def client(self):
        """ Create a new client with the configured options.

        :return: The created client.
        :rtype: module_utils.client.Client
        """
        options = {}
        for name in ['cli_path', 'config_dir', 'credential', 'credential_passphrase']:
            option = self.get_option(name)
            if option:
                options[name] = option
        return Client(**options)

    def get_option(self, name):
        """ Get the value of an option.

        The first of the following is returned:
        1. The value of the parameter in the playbook.
        2. The value of an environment variable SECRETHUB_<capitalized option name>.
        3. None

        :param name: The name of the option to retrieve.
        :return: The value of the retrieved option.
        :rtype: str | None
        """
        option = self.params.get(name)
        if not option:
            option = os.environ.get('SECRETHUB_'.format(name.upper()), None)
        return option
