FROM alpine:latest
LABEL org.opencontainers.image.authors="dmitry8912@gmail.com"
COPY sshd_config /etc/ssh/sshd_config
COPY run.sh /root/run.sh
RUN apk add openssh && chmod +x /root/run.sh
ENTRYPOINT ["/root/run.sh"]