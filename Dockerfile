FROM ubuntu:latest
MAINTAINER gorskimariusz "gorskimariusz13@gmail.com"

USER root

RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ raring main restricted universe multiverse" > /etc/apt/sources.list.d/ia32-libs-raring.list

# Install Python
RUN apt-get update
RUN apt-get install -y python3-pip python3-dev
RUN cd /usr/local/bin
RUN ln -s /usr/bin/python3 python
RUN pip3 install --upgrade pip

# Install prerequisites
ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get install -y libopencv-dev libtesseract-dev=3.02.02-1 git cmake build-essential libleptonica-dev
RUN apt-get install -y liblog4cplus-dev libcurl3-dev

# If using the daemon, install beanstalkd
RUN apt-get install -y beanstalkd

RUN mkdir -p /opt/

WORKDIR /opt

# Clone the latest code from GitHub
RUN git clone https://github.com/openalpr/openalpr.git

# Setup the build directory
RUN mkdir openalpr/src/build
RUN cd openalpr/src/build

# setup the compile environment
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc /opt/openalpr/src/

# compile the library
RUN make

# Install the binaries/libraries to your local system (prefix is /usr)
RUN make install

RUN mkdir /app

COPY . /app/

WORKDIR /app

ENV PYTHONPATH /app/:$PYTHONPATH

# Install dependencies
RUN pip3 install -r requirements.txt

#ENTRYPOINT ["tail -f /dev/null"]