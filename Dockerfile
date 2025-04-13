FROM python:3.10.17-alpine3.21
LABEL author="Hu Yao <hooyao@gmail.com>"
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && \
    apk --update add git openssh && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

WORKDIR /root

ADD requirements.txt ./
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir

ADD backup.py utils.py start.sh ./

CMD ["python", "backup.py", "-h"]


