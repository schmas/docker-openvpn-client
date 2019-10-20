# Docker OpenVPN Client
Build based on 
* [phusion/baseimage-docker](https://github.com/phusion/baseimage-docker)
* [haugene/docker-transmission-openvpn](https://github.com/haugene/docker-transmission-openvpn), even most of this README.

Docker container which runs OpenVPN client. Can be used as base image. Ex.: [Squid Proxy using OpenVPN](https://github.com/schmas/docker-openvpn-proxy) 
It bundles certificates and configurations for the following VPN providers:
* Anonine
* BTGuard
* Cryptostorm
* FrootVPN
* FrostVPN
* HideMe
* HideMyAss
* IntegrityVPN
* IPVanish
* Ivacy
* IVPN
* NordVPN
* Private Internet Access
* PrivateVPN
* PureVPN
* TigerVPN
* TorGuard (**July, 2019 with OpenVPN 2.4**)
* UsenetServerVPN

## Run container from Docker registry
The container is available from the Docker registry and this is the simplest way to get it.
To run the container use this command:

```
$ docker run --privileged  -d \
              -e "OPENVPN_PROVIDER=PIA" \
              -e "OPENVPN_CONFIG=Netherlands" \
              -e "OPENVPN_USERNAME=user" \
              -e "OPENVPN_PASSWORD=pass" \
              -p 1022:22 \
              dceschmidt/openvpn-client
```

You must set the environment variables `OPENVPN_PROVIDER`, `OPENVPN_USERNAME` and `OPENVPN_PASSWORD` to provide basic connection details.

The `OPENVPN_CONFIG` is an optional variable. If no config is given, a default config will be selected for the provider you have chosen.
Find available OpenVPN configurations by looking in the openvpn folder of the GitHub repository.

### Required environment options
| Variable | Function | Example |
|----------|----------|-------|
|`OPENVPN_PROVIDER` | Sets the OpenVPN provider to use. | `OPENVPN_PROVIDER=provider`. Supported providers are `PIA`, `BTGUARD`, `TIGER`, `FROOT`, `TORGUARD`, `NORDVPN`, `USENETSERVER`, `INTEGRITYVPN`, `IPVANISH`, `ANONINE`, `HIDEME`, `PUREVPN`, `HIDEMYASS`, `PRIVATEVPN`, `IVPN`, `IVACY` and `CRYPTOSTORM`|
|`OPENVPN_USERNAME`|Your OpenVPN username |`OPENVPN_USERNAME=asdf`|
|`OPENVPN_PASSWORD`|Your OpenVPN password |`OPENVPN_PASSWORD=asdf`|

### Network configuration options
| Variable | Function | Example |
|----------|----------|-------|
|`OPENVPN_CONFIG` | Sets the OpenVPN endpoint to connect to. | `OPENVPN_CONFIG=UK Southampton`|
|`OPENVPN_OPTS` | Will be passed to OpenVPN on startup | See [OpenVPN doc](https://openvpn.net/index.php/open-source/documentation/manuals/65-openvpn-20x-manpage.html) |
|`LOCAL_NETWORK` | Sets the local network that should have access. | `LOCAL_NETWORK=192.168.0.0/24`|

### SSH connection
This image has ssh connection enabled.
We can map the port for example with `-p 1022:22`.

For now it's only enabled the insecure private key from **[phusion/baseimage](https://github.com/phusion/baseimage-docker)**.

To connect:
```shell
# Download the insecure private key
curl -o insecure_key -fSL https://github.com/phusion/baseimage-docker/raw/master/image/services/sshd/keys/insecure_key
chmod 600 insecure_key

# Login to the container
ssh -i insecure_key root@localhost:1022

# Running a command inside the container
ssh -i insecure_key root@localhost:1022 echo hello world
```

## Known issues, tips and tricks

#### Use Google DNS servers
Some have encountered problems with DNS resolving inside the docker container.
This causes trouble because OpenVPN will not be able to resolve the host to connect to.
If you have this problem use dockers --dns flag to override the resolv.conf of the container.
For example use googles dns servers by adding --dns 8.8.8.8 --dns 8.8.4.4 as parameters to the usual run command.

#### Restart container if connection is lost
If the VPN connection fails or the container for any other reason loses connectivity, you want it to recover from it. One way of doing this is to set environment variable `OPENVPN_OPTS=--inactive 3600 --ping 10 --ping-exit 60` and use the --restart=always flag when starting the container. This way OpenVPN will exit if ping fails over a period of time which will stop the container and then the Docker deamon will restart it.

#### Questions?
If you are having issues with this container please submit an issue on GitHub.
Please provide logs, docker version and other information that can simplify reproducing the issue.
Using the latest stable verison of Docker is always recommended. Support for older version is on a best-effort basis.

## Adding new providers
If your VPN provider is not in the list of supported providers you could always create an issue on GitHub and see if someone could add it for you. But if you're feeling up for doing it yourself, here's a couple of pointers.

You clone this repository and create a new folder under "openvpn" where you put the .ovpn files your provider gives you. Depending on the structure of these files you need to make some adjustments. For example if they come with a ca.crt file that is referenced in the config you need to update this reference to the path it will have inside the container (which is /etc/openvpn/...). You also have to set where to look for your username/password.

There is a script called adjustConfigs.sh that could help you. After putting your .ovpn files in a folder, run that script with your folder name as parameter and it will try to do the changes descibed above. If you use it or not, reading it might give you some help in what you're looking to change in the .ovpn files.

Once you've finished modifying configs, you build the container and run it with OPENVPN_PROVIDER set to the name of the folder of configs you just created (it will be lowercased to match the folder names). And that should be it!

So, you've just added your own provider and you're feeling pretty good about it! Why don't you fork this repository, commit and push your changes and submit a pull request? Share your provider with the rest of us! :) Please submit your PR to the dev branch in that case.

## Building the container yourself
To build this container, clone the repository and cd into it.

### Build it:
```
$ cd <docker-openvpn-client>
$ docker build -t openvpn-client .
```
### Run it:
```
$ docker run --privileged  -d \
              -e "OPENVPN_PROVIDER=PIA" \
              -e "OPENVPN_CONFIG=Netherlands" \
              -e "OPENVPN_USERNAME=user" \
              -e "OPENVPN_PASSWORD=pass" \
              -p 1022:22 \
              openvpn-client
```

This will start a container as described in the "Run container from Docker registry" section.
