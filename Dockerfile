FROM python:3.7-slim-stretch

ARG BUILD_DATE
ARG VCS_REF

RUN echo $BUILD_DATE
RUN echo $VCS_REF

LABEL maintainer="Nick Badger <nbadger@mintel.com>" \
      org.opencontainers.image.title="k8s-notify" \
      org.opencontainers.image.description="Post Kubernetes Deployment Status To Flowdock" \
      org.opencontainers.url="https://github.com/mintel/k8s-notify" \
      org.opencontainers.source="https://github.com/mintel/k8s-notify.git" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.vendor="Mintel Group Ltd." \
      org.opencontainers.image.licences="MIT" \
      org.opencontainers.authors="Nick Badger <nbadger@mintel.com>" \
      org.opencontainers.image.created="$BUILD_DATE" \
      org.opencontainers.image.revision="$VCS_REF"

WORKDIR /app
COPY . ./

RUN pip install pipenv \
	&& pipenv install --system --deploy \
        && rm -rf /var/lib/apt/lists/*

USER 65534
ENTRYPOINT  [ "python", "-u", "/app/main.py" ]
CMD [ "--config=/etc/k8s-notify/config.yml" ]
