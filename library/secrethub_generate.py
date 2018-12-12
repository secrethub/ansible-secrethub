from ansible.module_utils.client import CLIInaccessible, GenerateError, ReadError
from ansible.module_utils.secrethub_base import BaseModule

DOCUMENTATION = '''
---
module: secrethub_generate

short_description: Generates a secret.

version_added: "2.6"

description:
    - "Generates a random secret that is stored in SecretHub."

options:
  path:
    description: The path of the secret.
    required: true
  length:
    description: The length of the secret.
    required: false
    default: 22
  symbols:
    description: A boolean indicating whether the secret is allowed to contain symbols.
    required: false
    default: false
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
# Generate a 22 characters long secret of random numbers and/or letters.
- name: Generate a random database password
  secrethub_generate:
    path: company/application/db_pass

# Register the generated secret for later usage.
- name: Generate a random database password
  secrethub_generate:
    path: company/application/db_pass
  register: db_pass
- name: Ensure a database user exists that authorizes using the generated secret.
    postgresql_user:
        db: {{ db_name }}
        name: "{{ db_user }}"
        password: "{{ db_pass.secret }}"
        priv: {{ db_priv }}
'''

RETURN = '''
secret:
  description: The generated secret.
  type: str
'''


class GenerateModule(BaseModule):

    def __init__(self):
        argument_spec = {
            'path': {
                'required': True,
                'type': "str",
            },
            'length': {
                'required': False,
                'type': "int",
                'default': 22,
            },
            'symbols': {
                'required': False,
                'type': "bool",
            }
        }
        super(GenerateModule, self).__init__(argument_spec)

    def run(self):
        try:
            secret = self.client().generate(
                self.params.get('path'),
                self.params.get('length'),
                self.params.get('symbols', False),
            )
            self.exit_json(
                changed=True,
                secret=secret,
            )
        except (CLIInaccessible, GenerateError) as e:
            self.fail_json(
                changed=False,
                msg=str(e),
            )
        except ReadError as e:
            self.fail_json(
                changed=True,
                msg=str(e),
            )


def main():
    GenerateModule().run()


if __name__ == '__main__':
    main()
