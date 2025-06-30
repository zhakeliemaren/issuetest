FROM centos:7

# 配置yum源为阿里云镜像
RUN mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak && \
    curl -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo && \
    yum clean all && \
    yum makecache

RUN yum install -y wget gcc make openssl-devel bzip2-devel libffi-devel zlib-devel
RUN wget -P /data/ob-tool https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz 
RUN cd /data/ob-tool && tar xzf Python-3.9.6.tgz
RUN cd /data/ob-tool/Python-3.9.6 && ./configure --enable-optimizations && make altinstall

ADD ./ /data/ob-robot/
RUN cd /data/ob-robot/ && \
    pip3.9 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /data/ob-robot/requirement.txt

# Install OpenSSH and a modern version of Git from the IUS repository.
# This avoids manual compilation, making the build faster and more reliable.
RUN yum install -y openssh-server && \
    yum install -y https://repo.ius.io/ius-release-el7.rpm && \
    yum install -y git236

ENV GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa'

WORKDIR /data/ob-robot
CMD if [ "$BOOT_MODE" = "app" ] ; then python3.9 main.py; fi
