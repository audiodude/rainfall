# syntax = docker/dockerfile:1

ARG NODE_VERSION=20.10.0
FROM node:${NODE_VERSION}-slim as fe-build

WORKDIR /usr/src/app

# Install packages needed to build node modules
RUN apt-get update -qq && \
  apt-get install -y build-essential pkg-config python-is-python3

# Install node modules
COPY --link rainfall-frontend/package.json rainfall-frontend/yarn.lock frontend/
RUN yarn install --frozen-lockfile

# Copy application code
COPY --link rainfall-frontend frontend

# Build frontend
WORKDIR /usr/src/app/frontend
# Use --production=false because we need the devDependencies to build
RUN yarn install --production=false --frozen-lockfile
RUN NODE_ENV=production yarn build

# Throw away build stage to reduce size of final image
FROM fe-build AS build

FROM ubuntu:24.04

# Install Faircamp dependencies
RUN apt-get update -qq && \
  apt-get install -y curl cmake ffmpeg gcc git libvips-dev

# Install Faircamp
WORKDIR /usr/src
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o rustup.sh && chmod a+x rustup.sh
RUN ./rustup.sh -y
RUN git clone https://codeberg.org/simonrepp/faircamp.git
WORKDIR faircamp
# NOTE: This is the faircamp version used in production. If it gets updated here, make sure
# to also update CI and local dev environments.
RUN git checkout tags/1.0.0
RUN $HOME/.cargo/bin/cargo install --features libvips --locked --path .

# Python app
RUN apt-get install -y python3.12 pipx
RUN pipx install pipenv
WORKDIR /usr/src
COPY ./Pipfile app/Pipfile
COPY ./Pipfile.lock app/Pipfile.lock

WORKDIR /usr/src/app
ENV PATH /root/.local/bin:/root/.cargo/bin:$PATH
RUN pipenv install --deploy --ignore-pipfile

COPY . .
COPY --from=build /usr/src/app/frontend ./rainfall-frontend

ENTRYPOINT ["./entrypoint.sh"]
