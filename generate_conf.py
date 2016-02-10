#! /usr/bin/env python

from __future__ import unicode_literals

from getpass import getpass


data = {
    'server': {
        'hosts': '',
    },
    'mailing': {
        'host': '',
        'port': '',
        'user': '',
        'password': '',
        'ssl': '',
        'tls': '',
        'from': '',
    },
    'sx': {
        'cluster': '',
        'is_secure': '',
        'port': '',
        'admin_key': '',
    }
}


def prompt(category, key, required, msg, prompt_func=raw_input,
           parser=lambda x: x.strip()):
    if required:
        msg = '(required) ' + msg
    else:
        msg = '(optional) ' + msg
    msg += ': '
    while True:
        value = prompt_func(msg)
        value = parser(value)
        if value or not required:
            break
    data[category][key] = value


def parse_bool(v):
    v = v.strip().lower()
    if not v:
        return ''
    if v[0] == 'y':
        return 'true'
    elif v[0] == 'n':
        return 'false'
    else:
        return ''


print 'Server configuration'.upper()
prompt('server', 'hosts', True,
       "Enter sxconsole hostname, e.g. 'localhost' or 'console.example.com'")

print 'E-mail configuration'.upper()
prompt('mailing', 'host', True,
       "Enter e-mail host, e.g. 'mail.example.com'")
prompt('mailing', 'port', False,
       "Enter the e-mail host port")
prompt('mailing', 'user', False,
       "Enter the e-mail host user")
prompt('mailing', 'password', False,
       "Enter the e-mail host user's password",
       prompt_func=getpass)
prompt('mailing', 'ssl', False,
       "Use ssl (y/n)",
       parser=parse_bool)
prompt('mailing', 'tls', False,
       "Use tls (y/n)",
       parser=parse_bool)
prompt('mailing', 'from', True,
       "Enter the 'from' e-mail address, e.g. 'noreply@example.com'")

print 'SX Cluster authentication'.upper()
prompt('sx', 'cluster', True,
       "Enter SX Cluster host, e.g. 'sx.example.com'")
prompt('sx', 'ssl', False,
       "Use ssl (y/n)",
       parser=parse_bool)
prompt('sx', 'port', False,
       "Enter SX Cluster port")
prompt('sx', 'admin_key', True,
       "Enter SX Cluster admin key")


def write_line(category, key):
    value = data[category][key]
    return '    {disable}{key}: {value}'.format(
        key=key, value=value, disable=('' if value else '# '))


conf = '\n'.join((
    "server:",
    "    # Server configuration",
    "    # sxconsole hostname or a list of hostnames, e.g.",
    "    #     console.example.com",
    "    # or",
    "    #     - console.example.com",
    "    #     - 127.0.0.1",
    write_line('server', 'hosts'),
    "    # (optional) path to sqlite3 databse",
    "    db: /data/sql/db.sqlite3",
    "app:",
    "# app settings",
    "    # (optional) set a default language. default is 'en'",
    "    # default_lang:",
    "    # (optional) By default, SX console will auto-detect your users " +
    "language.",
    "    # To enforce `default_lang`, enable this setting.",
    "    # force_default_lang: true",
    "    # (optional) enforce a minimal replica count",
    "    # min_replicas: 2",
    "mailing:",
    "# smtp settings",
    "    # The host to use for sending email",
    write_line('mailing', 'host'),
    "    # (optional) The port to use for the SMTP server",
    write_line('mailing', 'port'),
    "    # (optional) Username for the SMTP server",
    write_line('mailing', 'user'),
    "    # (optional) Password for the SMTP server",
    write_line('mailing', 'password'),
    "    # (optional) Whether to use SSL connection",
    write_line('mailing', 'ssl'),
    "    # (optional) Whether to use TLS connection",
    write_line('mailing', 'tls'),
    "    # The e-mail address which will be used as the sender",
    write_line('mailing', 'from'),
    "sx:",
    "# Cluster connection parameters",
    "    # SX Cluster name. will be used as host if ip_address is omitted",
    write_line('sx', 'cluster'),
    "    # (optional) ip address (or a list of ip addresses) of the cluster",
    "    # ip_addresses:",
    "    # (optional) toggle ssl. default is true",
    write_line('sx', 'is_secure'),
    "    # (optional) specifies a custom connection port",
    write_line('sx', 'port'),
    "    # SX admin user authentication - either is required:",
    "    # base64-encoded user key",
    write_line('sx', 'admin_key'),
    "    # path to a file with encoded user key",
    "    # admin_key_path:",
    "    # Extra configuration parameters",
    "    # (optional) toggle ssl certificate validation. default is true",
    "    # verify_ca:",
    "    # (optional) path to a custom certificate. implies verify_ca",
    "    # certificate:",
    "carbon:",
    "    carbon_host: CARBON_ADDR",
    "    port: 2004",
    "    whisper_dir: /var/lib/graphite/storage/whisper/"))

with open('/data/sxconsole-lite/conf_defaults.yaml', 'w') as f:
    f.write(conf)
