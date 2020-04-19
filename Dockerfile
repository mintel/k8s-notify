FROM python:3.7-slim-stretch

ARG BUILD_DATE
ARG VCS_REF

RUN echo $BUILD_DATE
RUN echo $VCS_REF

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/mintel/k8s-notify.git" \
      org.label-schema.schema-version="0.1.0" \
      org.label-schema.name="k8s-notify" \
      org.label-schema.description="Post Kubernetes Deployment Status To Flowdock" \
      org.label-schema.vendor="Mintel Group Ltd." \
      maintainer="Nick Badger <nbadger@mintel.com>"

WORKDIR /app
COPY . ./

RUN pip install pipenv \
	&& pipenv install --system --deploy \
        && rm -rf /var/lib/apt/lists/*

USER 65534
ENTRYPOINT  [ "python", "-u", "/app/main.py" ]
CMD [ "--config=/etc/k8s-notify/config.yml "]
