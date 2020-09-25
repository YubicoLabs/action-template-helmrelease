FROM alpine/helm:3.3.4 AS helm

FROM alpine:3.12 AS yq
RUN apk add curl
RUN curl -L -O https://github.com/mikefarah/yq/releases/download/3.4.0/yq_linux_amd64
RUN echo "f6bd1536a743ab170b35c94ed4c7c4479763356bd543af5d391122f4af852460  yq_linux_amd64" > checksums
RUN sha256sum -c checksums
RUN mv yq_linux_amd64 /usr/bin/yq
RUN chmod +x /usr/bin/yq

FROM alpine:3.12
COPY --from=helm /usr/bin/helm /usr/bin/helm
COPY --from=yq /usr/bin/yq /usr/bin/yq
COPY template_helmrelease /usr/bin/template_helmrelease
ENTRYPOINT [ "template_helmrelease" ]
