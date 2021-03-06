FROM alpine/helm:3.3.4 AS helm

FROM alpine:3.12
RUN apk add curl && \
    curl -L -O https://github.com/mikefarah/yq/releases/download/3.4.0/yq_linux_amd64 && \
    echo "f6bd1536a743ab170b35c94ed4c7c4479763356bd543af5d391122f4af852460  yq_linux_amd64" > checksums && \
    sha256sum -c checksums && \
    mv yq_linux_amd64 /usr/bin/yq && \
    chmod +x /usr/bin/yq
COPY --from=helm /usr/bin/helm /usr/bin/helm
COPY template_helmrelease /usr/bin/template_helmrelease
ENTRYPOINT [ "template_helmrelease" ]
