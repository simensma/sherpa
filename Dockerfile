FROM turistforeningen/python-ucs4:2.7

ENV HOME /root

RUN apt-get update
RUN apt-get -y --no-install-recommends install \
    libodbc1 unixodbc unixodbc-dev freetds-common tdsodbc \
    libgeos-dev gettext libexiv2-dev libmemcached-dev \
    python-libxml2 python-libxslt1 python-pyexiv2 libboost-python-dev && \

    # freetype2 symlink required for building Pillow
    ln -s /usr/include/freetype2 /usr/include/freetype2/freetype && \

    # sooo, pyexiv2 isn't installing to the expected location
    ln -s /usr/lib/python2.7/dist-packages/pyexiv2 /usr/local/lib/python2.7/site-packages/pyexiv2 && \
    ln -s /usr/lib/python2.7/dist-packages/libexiv2python.so /usr/local/lib/python2.7/site-packages/libexiv2python.so

ADD build/ /build
RUN mv -v /build/odbcinst.ini /etc/odbcinst.ini && \
    chmod 644 /etc/odbcinst.ini && \
    mkdir /sherpa

WORKDIR /sherpa

# Install python packages
ADD requirements.txt /sherpa/requirements.txt
RUN pip install --src /tmp --allow-external pyodbc --allow-unverified pyodbc -r requirements.txt

ADD requirements_dev.txt /sherpa/requirements_dev.txt
RUN pip install --src /tmp -r requirements_dev.txt --ignore-installed

ADD manage.py /sherpa/manage.py
ADD gunicorn.py /sherpa/gunicorn.py
CMD ["gunicorn -c gunicorn.py"]

ADD . /sherpa/

RUN apt-get -y autoclean && apt-get -y autoremove && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8000
