#!/bin/sh
ssh-keygen -A
adduser -D $SSH_USER && echo "$SSH_USER:$SSH_PASS" | chpasswd
printf "\nPermitOpen $TO_HOST:3389" >> /etc/ssh/sshd_config
/usr/sbin/sshd -D