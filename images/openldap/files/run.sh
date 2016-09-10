#!/bin/sh

RUNCMD=$1

if [ $RUNCMD != "start" -a $RUNCMD != "start_ssl" -a $RUNCMD != "version" -a $RUNCMD != "help" -a $RUNCMD != "init-vol" ]; then
        echo "Unsupported command" > /dev/stderr
        exit 1
fi

if [ $RUNCMD == "help" ]; then
        echo "Available commands:"
        echo
        echo "  start        launch slapd (ldap://)"
        echo "  start_ssl    launch slapd (ldap:// and ldaps://)"
        echo "  version      show slapd version"
        echo "  init-vol     setup volume content for /etc/openldap and /var/lib/openldap"
        echo "  help         show this help"
        echo
        exit 0
fi

if [ $RUNCMD == "init-vol" ]; then
        cp -a /etc/openldap.orig/* /etc/openldap
        if [ ! -d /var/lib/openldap/openldap-data ]; then
                mkdir -p /var/lib/openldap/openldap-data
                chmod 700 /var/lib/openldap/openldap-data
                chown ldap.ldap /var/lib/openldap/openldap-data
        fi
        if [ ! -d /var/lib/openldap/run ]; then
                mkdir -p /var/lib/openldap/run
                chmod 700 /var/lib/openldap/run
                chown ldap.ldap /var/lib/openldap/run
        fi
        echo "Volumes have been initialized"
        exit 0
fi

if [ $RUNCMD == "version" ]; then
        /usr/sbin/slapd -V
        exit 0
fi

if [ $RUNCMD == "start" ]; then
        ulimit -n 8192 && /usr/sbin/slapd -d 256 -u ldap -g ldap
fi

if [ $RUNCMD == "start_ssl" ]; then
        ulimit -n 8192 && /usr/sbin/slapd -d 256 -u ldap -g ldap -h "ldap:// ldaps://"
fi
