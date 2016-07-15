# OpenVPN Client
#
# based on https://github.com/haugene/docker-transmission-openvpn
#
# Version 0.0.1
#
# See
# https://github.com/phusion/baseimage-docker/blob/master/Changelog.md
# for a list of version numbers.

FROM phusion/baseimage:latest
MAINTAINER Diego Schmidt <dceschmidt@gmail.com>

# Evironment variables
ENV DEBIAN_FRONTEND=noninteractive \
    OPENVPN_USERNAME=**None** \
    OPENVPN_PASSWORD=**None** \
    OPENVPN_PROVIDER=**None**


# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]


# Update packages and install software
RUN apt-get update \
    && apt-get install -y openvpn inetutils-traceroute inetutils-ping \
    && curl -L https://github.com/jwilder/dockerize/releases/download/v0.2.0/dockerize-linux-amd64-v0.2.0.tar.gz | tar -C /usr/local/bin -xzv \
    && rm -rfv dockerize-linux-amd64-v0.2.0.tar.gz \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \


# Enabling SSH
RUN rm -f /etc/service/sshd/down

# Enabling the insecure key permanently
RUN /usr/sbin/enable_insecure_key

# Expose port and run
EXPOSE 22

# Add configuration and scripts
ADD openvpn /etc/openvpn

# Add to runit
#RUN mkdir /etc/service/openvpn
#ADD openvpn/start.sh /etc/service/openvpn/run
#RUN chmod +x /etc/service/openvpn/run