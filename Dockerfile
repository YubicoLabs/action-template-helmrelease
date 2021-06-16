FROM alpine/helm:3.5.4 AS helm

FROM alpine:3.13
RUN apk add python3 py3-pip && pip3 install 'pyyaml>=5.4,<6.0'
COPY --from=helm /usr/bin/helm /usr/local/bin/helm
COPY template_helmrelease.py /usr/local/bin/template_helmrelease
ENTRYPOINT [ "template_helmrelease" ]
