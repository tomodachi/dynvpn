FROM ubuntu:16.04

MAINTAINER Mateusz Mojsiejuk tomodachi@fishface.se

# Install required packages
RUN apt-get update && apt-get install -y openvpn easy-rsa nftables python2.7

# Inject needed files
COPY ./scripts /etc/openvpn/scripts
COPY ./server-vpn.conf /etc/openvpn/
COPY ./vars /etc/openvpn/easy-rsa/
COPY ./openssl-1.0.0.cnf /etc/openvpn/easy-rsa/
COPY ./init-vpn /etc/openvpn/scripts/
RUN chmod 755 /etc/openvpn/scripts/init-vpn

# Generate key and CA for VPN server
RUN cp -rv /usr/share/easy-rsa /etc/openvpn/ \
&& mkdir /etc/openvpn/easy-rsa/keys \
&& ln -s /etc/openvpn/easy-rsa/keys /etc/openvpn/keys \
&&  openvpn --genkey --secret /etc/openvpn/keys/static.key \


&& /bin/bash -c "cd /etc/openvpn/easy-rsa && source /etc/openvpn/easy-rsa/vars && ./clean-all && ./build-ca --batch && ./build-key-server --batch server" \

&& openssl dhparam -out /etc/openvpn/keys/dh1024.pem 1024 \
# Generate VPN client files
# workaround since non interactive mode for build-key is a bit flaky
&& sed -i 's/KEY_CN=changeme/KEY_CN=dynvpn-test/' /etc/openvpn/easy-rsa/vars \
&&  /bin/bash -c "cd /etc/openvpn/easy-rsa && source ./vars && ./build-key --batch dynvpn-test" \

# VPN client config
COPY ./client-vpn.conf /etc/openvpn/easy-rsa/keys/


EXPOSE 1194

# RUN /etc/openvpn/scripts/dynvpn.nftables only works in privileged mode
# so we do that and start openvpn upon launching container
CMD ["/etc/openvpn/scripts/init-vpn"]
