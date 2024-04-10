FROM centos:7

RUN yum update -y && \
    yum install -y wget gcc make openssl-devel bzip2-devel libffi-devel zlib-devel
RUN wget -P /data/ob-tool https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz 
RUN cd /data/ob-tool && tar xzf Python-3.9.6.tgz
RUN cd /data/ob-tool/Python-3.9.6 && ./configure --enable-optimizations && make altinstall

ADD ./ /data/ob-robot/
RUN cd /data/ob-robot/ && \
    pip3.9 install -r /data/ob-robot/requirement.txt

RUN yum install -y git openssh-server 

ENV GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa'
RUN yum install -y autoconf gettext && \
    wget http://github.com/git/git/archive/v2.32.0.tar.gz && \
    tar -xvf v2.32.0.tar.gz && \
    rm -f v2.32.0.tar.gz && \
    cd git-* && \
    make configure && \
    ./configure --prefix=/usr && \
    make -j16 && \
    make install

WORKDIR /data/ob-robot
CMD if [ "$BOOT_MODE" = "app" ] ; then python3.9 main.py; fi
