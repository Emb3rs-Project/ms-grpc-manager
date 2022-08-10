FROM ghcr.io/emb3rs-project/embers-base:latest as build

# creating the environment
COPY environment-py39.yml .
RUN --mount=type=cache,target=/opt/conda/pkgs mamba env create -f environment-py39.yml

# Installing Conda Pack
RUN --mount=type=cache,target=/opt/conda/pkgs conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n ms-grpc-manager -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack

FROM python:3.10-slim as runtime

# setup config
ENV GROUP_ID=1000 \
    USER_ID=1000

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

COPY --from=build /venv /venv

# Configuring app
WORKDIR /app
COPY . .

ENV PYTHONPATH=ms-grpc/plibs:module

EXPOSE 50051

SHELL [ "/bin/bash", "-c" ]
RUN echo 'source /venv/bin/activate' >> ~/.bashrc && source ~/.bashrc

ENTRYPOINT source /venv/bin/activate && \
    PYTHONPATH=ms-grpc/plibs:module \
    python -u server.py
