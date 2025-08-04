############################################################
# Dockerfile to build Django Development Environment

# Based on Ubuntu

############################################################
# syntax=docker/dockerfile:1

# 设置镜像基于ubuntu
FROM ubuntu:22.04

LABEL maintainer="daibeisi <heyares@163.com>"

# 设置环境变量，防止交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /workspace

# 暴露端口：SSH(22), HTTP(80), HTTP(8000)
EXPOSE 22 80 8000

# 启动容器时执行的命令
CMD ["/bin/bash"]