#
# Dockerfile - Arcus Memcached
#

# 기본 이미지
FROM     ubuntu:14.04

# 기본 저장소 변경
RUN sed -i 's/kr.archive.ubuntu.com/ftp.daumkakao.com/g' /etc/apt/sources.list

# 최신 패키지 업데이트 및 필요 패키지 설치
RUN apt-get clean
RUN apt-get update && apt-get install -y curl openssh-server supervisor

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

# Arcus Memcached가 실행 될 사용자 생성 및 설정
RUN useradd -M -s /sbin/nologin memcached \
 && mkdir -p /var/run/memcached && chown memcached:memcached /var/run/memcached

# Supervisor 설정
RUN mkdir -p /var/log/supervisor
ADD conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# SSH 설정
RUN mkdir /root/.ssh && mkdir /var/run/sshd
RUN sed -i 's/without-password/yes/g' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config

# 루트 비밀번호 설정
RUN echo 'root:memcached' |chpasswd

# 포트 설정
EXPOSE 22 2181 11211 11212

# 명령어 실행
CMD ["/usr/bin/supervisord"]

