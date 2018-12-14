[![codeclimate maintainability badge](https://api.codeclimate.com/v1/badges/7649852aa7650e331b2a/maintainability)](https://codeclimate.com/github/secrethub/ansible-secrethub/maintainability)
[![codacy badge](https://api.codacy.com/project/badge/Grade/297a2289bff74c49be800d973eea2923)](https://www.codacy.com/app/SecretHub/ansible-secrethub)
[![codebeat badge](https://codebeat.co/badges/78df7e54-0cc2-4672-a843-a49c92135892)](https://codebeat.co/projects/github-com-secrethub-ansible-secrethub-master)
[![codeclimate test coverage badge](https://api.codeclimate.com/v1/badges/7649852aa7650e331b2a/test_coverage)](https://codeclimate.com/github/secrethub/ansible-secrethub/test_coverage)

# SecretHub Ansible modules

## SecretHub

To use the SecretHub modules, an account on [SecretHub](https://secrethub.io) is needed.
See [the guide](https://secrethub.io/docs/getting-started/) on how to get started with SecretHub.

## Integration

To use the SecretHub modules in your playbooks, symlink or copy the `library` and `module_utils` directories to the root directory of your ansible project (next to your playbooks).

```
$ git clone git@github.com:secrethub/ansible-secrethub.git
$ ln -s <path to ansible-secrethub>/library <ansible project root>/library
$ ln -s <path to ansible-secrethub>/module_utils <ansible project root>/module_utils
```

## Usage

### secrethub_cli

Installs the SecretHub CLI.

##### Parameters

|Parameter| Required | Choices| Default | Comments|
|---|---|---|---|---|
| install_dir | no | | | The path where the CLI is installed. This defaults to `/usr/local/secrethub/` on Unix systems and `C://Program Files/SecretHub/` on Windows. |
| state | no | present<br>absent | present | The state present implies that the CLI should be installed if necessary. Absent implies that the CLI should be uninstalled if present. |
| version | no | | latest | The version of the CLI that should be installed. When state is absent, version will be ignored. |

##### Return values

| Key  | Description |
|---|---|
| bin_path | The absolute path to the location of the installed binary. |
| install_dir | The absolute path to the directory in which the secrethub binary is installed. Add this directory to the PATH to make the CLI globally accessible. |
| version | The currently installed version of the SecretHub CLI. |

##### Examples

``` {.sourceCode .yaml+jinja}
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
```

### secrethub_read

Reads a secret that is stored in SecretHub.

##### Parameters

| Parameter | Required | Choices | Default | Comments |
|---|---|---|---|---|
| path | yes | | | The path of the secret. |
| cli_path | no | | | The path to the CLI binary to use. To set this globally the environment variable `SECRETHUB_CLI_PATH` can be set. When omitted, a default of `/usr/local/secrethub/secrethub` or `C:/Program Files/SecretHub/secrethub.exe` (on Windows) is used. |
| config_dir | no | | | The configuration directory to use. To set this globally the environment variable SECRETHUB_CONFIG_DIR can be set. This is where we look for a credential when it is not supplied trough the module. Defaults to a .secrethub directory in the home directory. |
| credential | no | | | The credential used to decrypt your accounts encryption key. To set this globally the environment variable SECRETHUB_CREDENTIAL can be set. When omitted, the credential must be stored in the configuration directory. |
| credential_passphrase | no | | | The passphrase to decrypt the credential with. To set this globally the environment variable SECRETHUB_CREDENTIAL_PASSPHRASE can be set. |

##### Return values

| Key  | Description |
|---|---|
| secret | The secret value stored in the given path. |

###### Examples

``` {.sourceCode .yaml+jinja}
# Read a secret.
- name: Read the database password
  secrethub_read:
    path: company/application/db_pass
  register: db_pass
```

### secrethub_write

Save a secret in SecretHub.

##### Parameters

| Parameter | Required | Choices | Default | Comments |
|---|---|---|---|---|
| path | yes | | | The path of the secret. |
| value | yes | | | The value of the secret. |
| cli_path | no | | | The path to the CLI binary to use. To set this globally the environment variable `SECRETHUB_CLI_PATH` can be set. When omitted, a default of `/usr/local/secrethub/secrethub` or `C:/Program Files/SecretHub/secrethub.exe` (on Windows) is used. |
| config_dir | no | | | The configuration directory to use. To set this globally the environment variable SECRETHUB_CONFIG_DIR can be set. This is where we look for a credential when it is not supplied trough the module. Defaults to a .secrethub directory in the home directory. |
| credential | no | | | The credential used to decrypt your accounts encryption key. To set this globally the environment variable SECRETHUB_CREDENTIAL can be set. When omitted, the credential must be stored in the configuration directory. |
| credential_passphrase | no | | | The passphrase to decrypt the credential with. To set this globally the environment variable SECRETHUB_CREDENTIAL_PASSPHRASE can be set. |

##### Return values

| Key  | Description |
|---|---|
| secret | The secret value stored in the given path. |

###### Examples

``` {.sourceCode .yaml+jinja}
# Write a secret.
# The db_pass variable is registered by an earlier process.
# To generate a new password, use the secrethub_generate module.
- name: Store the database password
  secrethub_write:
    path: company/application/db_pass
    value: {{ db_pass }}
```

### secrethub_generate

Generates a random secret that is stored in SecretHub.

##### Parameters

| Parameter | Required | Choices | Default | Comments |
|---|---|---|---|---|
| path | yes | | | The path of the secret. |
| length | no | | 22 | The length of the secret. |
| symbols | no | yes<br>no | no | A boolean indicating whether the secret is allowed to contain symbols. |
| cli_path | no | | | The path to the CLI binary to use. To set this globally the environment variable `SECRETHUB_CLI_PATH` can be set. When omitted, a default of `/usr/local/secrethub/secrethub` or `C:/Program Files/SecretHub/secrethub.exe` (on Windows) is used. |
| config_dir | no | | | The configuration directory to use. To set this globally the environment variable SECRETHUB_CONFIG_DIR can be set. This is where we look for a credential when it is not supplied trough the module. Defaults to a .secrethub directory in the home directory. |
| credential | no | | | The credential used to decrypt your accounts encryption key. To set this globally the environment variable SECRETHUB_CREDENTIAL can be set. When omitted, the credential must be stored in the configuration directory. |
| credential_passphrase | no | | | The passphrase to decrypt the credential with. To set this globally the environment variable SECRETHUB_CREDENTIAL_PASSPHRASE can be set. |

##### Examples

``` {.sourceCode .yaml+jinja}
# Generate a 22 characters long secret of random numbers and/or letters.
- name: Generate a random database password
  secrethub_generate:
    path: company/infra/app/db_pass
```

##### Return values

| Key  | Description |
|---|---|
| secret | The generated secret. |
