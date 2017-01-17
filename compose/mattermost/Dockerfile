# Copyright (c) 2016 Mattermost, Inc. All Rights Reserved.
# See License.txt for license information.
FROM mysql:5.7

# Install ca-certificates to support TLS of Mattermost v3.5
RUN apt-get update && apt-get install -y ca-certificates

#
# Configure SQL
#

ENV MYSQL_ROOT_PASSWORD=mostest
ENV MYSQL_USER=mmuser
ENV MYSQL_PASSWORD=mostest
ENV MYSQL_DATABASE=mattermost_test

#
# Configure Mattermost
#
WORKDIR /mm

# Copy over files
ADD https://releases.mattermost.com/3.6.0/mattermost-3.6.0-linux-amd64.tar.gz archive.tgz
RUN tar -zxvf ./archive.tgz
ADD config_docker.json ./mattermost/config/config.json
ADD docker-entry.sh .

RUN chmod +x ./docker-entry.sh
ENTRYPOINT ["./docker-entry.sh"]

# Create default storage directory
RUN mkdir /mm/mattermost-data
# FIX HERE
VOLUME /mm/mattermost-data

# Ports
EXPOSE 8065
