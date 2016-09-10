FROM alpine

MAINTAINER Giacomo Lozito

COPY files/run.sh /run.sh

RUN apk update && apk add openldap openldap-clients openldap-back-hdb openldap-back-bdb ldapvi && cp -a /etc/openldap /etc/openldap.orig && chmod 755 /run.sh

EXPOSE 389 636
VOLUME ["/etc/openldap","/var/lib/openldap"]

ENTRYPOINT ["/run.sh"]
CMD ["start"]
