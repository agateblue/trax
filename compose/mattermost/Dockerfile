# Copyright (c) 2016 Mattermost, Inc. All Rights Reserved.
# See License.txt for license information.
FROM debian:8

# Install ca-certificates to support TLS of Mattermost v3.5
RUN apt-get update && apt-get install -y ca-certificates

#
# Configure SQL
#


#
# Configure Mattermost
#
WORKDIR /mm

# Copy over files
ADD https://releases.mattermost.com/3.6.0/mattermost-3.6.0-linux-amd64.tar.gz archive.tgz
RUN tar -zxvf ./archive.tgz
ADD config_docker.json ./mattermost/config/config.json

WORKDIR /mm/mattermost
ENTRYPOINT ["./bin/platform"]

# Create default storage directory
RUN mkdir /mm/mattermost-data
# FIX HERE
VOLUME /mm/mattermost-data

# Ports
EXPOSE 8065
