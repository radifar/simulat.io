FROM frolvlad/alpine-miniconda3:python3.7

# python envs
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# For psutil
RUN apk add --no-cache gcc libc-dev linux-headers bash nano

# Conda environment
COPY ./environment.yml /
RUN conda env update -n base -f ./environment.yml

# Copy script
COPY ./scripts/entrypoint.sh ./scripts/start.sh ./scripts/gunicorn.sh /

WORKDIR /app
