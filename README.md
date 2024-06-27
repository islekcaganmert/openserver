# OpenServer

OpenServer is a server software for TheProtocols.

## Features

1. Complete compatibility with TheProtocols 3.0-3.1
2. Easy to use setup wizard
3. Encrypted communication
4. Exportable user accounts

## Installation

1. Download the latest version of OpenServer from the [releases page](https://github.com/islekcaganmert/openserver/releases)

2. Install it via pip:

```bash
pip install openserver-*.tar.gz
```

> [!TIP]
> I recommend using a virtual environment with name of the release. This will provide rollback capability and lower the risk of package conflicts.

3. Create an empty folder for your server:

```bash
mkdir myserver
cd myserver
```

> [!WARNING]
> You must use a completely blank folder. OpenServer will create files in this folder. It will not use if any other files or folder exist, including virtualenv.

4. Run setup wizard:

```bash
python3 -m openserverctl
```

> [!NOTE]
> If you want to have a warranty, you must purchase a license key. Please [email me](mailto:islekcaganmert@gmail.com) for more information.

5. Start the server:

```bash
python3 -m openserver config.yaml
```

6. Open your client and switch to your network. You can choose a client from [client directory](https://github.com/islekcaganmert/TheProtocols/blob/main/Directory/Clients.md).

7. Create a new user with standard permissions.