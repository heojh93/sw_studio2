#
# Dockerfile - Arcus
# 

# 기본 이미지
FROM     ubuntu:14.04

# 기본 저장소 변경
RUN sed -i 's/archive.ubuntu.com/ftp.jaist.ac.jp/g' /etc/apt/sources.list

# 최신 패키지 업데이트 및 Arcus를 빌드하기 위한 패키지 설치
RUN apt-get update && apt-get install -y supervisor openssh-server aptitude net-tools iputils-ping nano curl \
 git netcat build-essential make gcc g++ autoconf automake libtool libextutils-pkgconfig-perl libcppunit-dev python2.7-dev python-setuptools subversion

# 기본 소스 디렉토리 설정
ENV SRC_DIR /opt

# JDK 설치
ENV JAVA_HOME /usr/lib/jvm/java-1.7.0-openjdk-amd64
ENV PATH $PATH:$JAVA_HOME/bin
RUN apt-get install -y openjdk-7-jdk \
 && echo '' >> /etc/profile \
 && echo '# JDK' >> /etc/profile \
 && echo "export JAVA_HOME=$JAVA_HOME" >> /etc/profile \
 && echo 'export PATH="$PATH:$JAVA_HOME/bin"' >> /etc/profile \
 && echo '' >> /etc/profile

# ANT 설치
ENV ANT_HOME /usr/share/ant
ENV PATH $PATH:$ANT_HOME/bin
RUN apt-get install -y ant \
 && echo '' >> /etc/profile \
 && echo '# ANT' >> /etc/profile \
 && echo "export ANT_HOME=$ANT_HOME" >> /etc/profile \
 && echo 'export PATH="$PATH:$ANT_HOME/bin"' >> /etc/profile \
 && echo '' >> /etc/profile

# Arcus 빌드
RUN cd $SRC_DIR && git clone https://github.com/ruo91/arcus.git \
 && cd arcus/scripts && ./build.sh
ADD conf/studio.json $SRC_DIR/arcus/scripts/conf/studio.json

# SSH Public Key 생성
RUN ssh-keygen -t dsa -P '' -f "/root/.ssh/id_dsa"
RUN cat /root/.ssh/id_dsa.pub >> /root/.ssh/authorized_keys
RUN chmod 644 /root/.ssh/authorized_keys

# Supervisor 설정
RUN mkdir -p /var/log/supervisor
ADD conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# SSH 설정
RUN mkdir /var/run/sshd
RUN sed -i 's/without-password/yes/g' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config

# 루트 비밀번호 설정
RUN echo 'root:arcus' |chpasswd

# 포트 설정
EXPOSE 22

# 명령 실행
CMD ["/usr/bin/supervisord"]

