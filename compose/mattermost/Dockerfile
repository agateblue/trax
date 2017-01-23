# Copyright (c) 2016 Mattermost, Inc. All Rights Reserved.
# See License.txt for license information.
FROM mysql:5.7

# Install ca-certificates to support TLS of Mattermost v3.5
RUN apt-get update && apt-get install -y ca-certificates curl

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

RUN mkdir -p /mattermost/data
VOLUME /mattermost/data

RUN curl https://releases.mattermost.com/3.6.1/mattermost-team-3.6.1-linux-amd64.tar.gz | tar -xvz

RUN rm /mattermost/config/config.json

WORKDIR /mattermost
ADD docker-entry.sh .
RUN chmod +x ./docker-entry.sh
ENTRYPOINT ["./docker-entry.sh"]

EXPOSE 8065
