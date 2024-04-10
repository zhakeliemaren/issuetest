FROM reg.docker.alibaba-inc.com/obvos/python3:3.9.2

COPY ./requirement.txt /tmp/requirement.txt
RUN /usr/local/bin/pip3.9 install -r /tmp/requirement.txt; rm -f /tmp/requirement.txt