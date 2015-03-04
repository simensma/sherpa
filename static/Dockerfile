FROM turistforeningen/ruby-iojs:2.1-1.4

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY Gemfile /usr/src/app/
RUN bundle install

COPY package.json /usr/src/app/
RUN NODE_ENV=production npm --loglevel info install

RUN apt-get -y autoclean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

