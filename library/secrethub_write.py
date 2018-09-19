from ansible.module_utils.client import CLIInaccessible, WriteError
from ansible.module_utils.secrethub_base import BaseModule

DOCUMENTATION = '''
---
module: secrethub_write

short_description: Store a secret.

version_added: "2.6"

description:
    - "Save a secret in SecretHub."

options:
  path:
    description: The path of the secret.
    required: true
  value:
    description: The value of the secret.
    required: true
  cli_path:
    description:
        The path to the CLI binary to use. To set this globally the environment variable SECRETHUB_CLI_PATH can be set.
        When omitted, a default of /usr/local/secrethub/secrethub or
        C:/Program Files/SecretHub/secrethub.exe (on Windows) is used.
    required: false
  config_dir:
    description:
        The configuration directory to use. To set this globally the environment variable SECRETHUB_CONFIG_DIR can be
        set. This is where we look for a credential when it is not supplied trough the module. Defaults to a .secrethub
        directory in the home directory.
    required: false
  credential:
    description:
        The credential used to decrypt your accounts encryption key. To set this globally the environment variable
        SECRETHUB_CREDENTIAL can be set. When omitted, the credential must be stored in the configuration directory.
    required: false
  credential_passphrase:
    description:
        The passphrase to decrypt the credential with. To set this globally the environment variable
        SECRETHUB_CREDENTIAL_PASSPHRASE can be set.
    required: false

author:
    - Simon Barendse (@simonbarendse)
    - Marc Mackenbach (@mackenbach)
'''

EXAMPLES = '''
# Write a secret.
- name: Store the database password
  secrethub_write:
    path: company/application/db_pass
    value: {{ db_pass }}
'''

RETURN = '''
secret:
  description: The secret that is stored in the given path.
  type: str
'''


class WriteModule(BaseModule):

    def __init__(self):
        argument_spec = {
            'path': {
                'required': True,
                'type': "str",
            },
            'value': {
                'required': True,
                'type': "str",
                'no_log': True,
            }
        }
        super(WriteModule, self).__init__(argument_spec=argument_spec)

    def run(self):
        try:
            self.exit_json(
                changed=True,
                secret=self.client().write(
                    self.params.get('path'),
                    self.params.get('value'),
                )
            )
        except (CLIInaccessible, WriteError) as e:
            self.fail_json(
                changed=False,
                msg=str(e),
            )


def main():
    WriteModule().run()


if __name__ == '__main__':
    main()
