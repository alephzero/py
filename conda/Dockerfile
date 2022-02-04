FROM ubuntu:20.04

RUN apt update && DEBIAN_FRONTEND="noninteractive" apt install -y \
    wget
# g++ git make wget zlib1g-dev

RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda.sh && \
    /bin/bash Miniconda.sh -b -p /opt/conda && \
    rm Miniconda.sh
ENV PATH=/opt/conda/bin:$PATH

RUN conda install conda-build

COPY . /py/

RUN cd /py/conda/ && \
    conda build -c conda-forge .

# RUN mkdir -p /py/channel/linux-64 && \
#     cp /opt/conda/conda-bld/linux-64/alephzero-0.3.10-py39_0.tar.bz2 /channel/linux-64 && \
#     mamba index /py/channel

# mamba install -c file:///py/channel alephzero
