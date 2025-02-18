#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# A script to update the environment
# Copyright (C) 2006-2011 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import os
import sys
import getopt

header = "### This file is automatically generated by update-environment"

header_note = """
#
# Please do not edit this file directly. If you want to change
# anything, please take a look at the files in /etc/env.d
# and read the Pardus initialization system documentation.
#
# Bu otomatik olarak oluşturulmuş bir dosyadır.
# Lütfen bu dosyayı elle değiştirmeyin. Değiştirmek istediğiniz
# şeyler varsa, /etc/env.d dizinindeki dosyalara ve Pardus
# açılış sistemi belgesine bakın.
#
"""

specials = (
    "KDEDIRS",
    "PATH",
    "CLASSPATH",
    "MANPATH",
    "INFOPATH",
    "ROOTPATH",
    "CONFIG_PROTECT",
    "CONFIG_PROTECT_MASK",
    "PRELINK_PATH",
    "PRELINK_PATH_MASK",
    "PYTHONPATH",
    "ADA_INCLUDE_PATH",
    "ADA_OBJECTS_PATH",
    "PKG_CONFIG_PATH"
)


def read_env_d(envdir):
    d = {}

    paths = []
    for name in os.listdir(envdir):
        path = os.path.join(envdir, name)
        # skip dirs (.svn, .cvs, etc)
        if os.path.isdir(path):
            continue
        # skip backup and version control files
        if name.endswith("~") or name.endswith(".bak") or name.endswith(",v"):
            continue
        # skip pisi's config file backups
        # .oldconfig is obsolete, but checked anyway cause it may still exist at old systems
        if name.endswith(".oldconfig") or name.endswith(".newconfig"):
            continue
        paths.append(path)
    paths.sort()

    for path in paths:
        for line in open(path):
            if line == "" or line.startswith("#"):
                continue

            line = line.rstrip("\n")
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]

                # Merge for special variables, override for others
                if key in specials:
                    if key in d:
                        d[key].extend(value.split(":"))
                    else:
                        d[key] = value.split(":")
                else:
                    d[key] = value

    return d


def generate_profile_env(envdict, format='export %s="%s"\n'):
    profile = ""
    keys = list(envdict.keys())
    keys.sort()
    for key in keys:
        tmp = envdict[key]
        if isinstance(tmp, list):
            tmp = ":".join(tmp)
        profile += format % (key, tmp)
    return header + header_note + profile


def update_file(path, content):
    f = open(path, "w", encoding='utf-8')
    f.write(content)
    f.close()


def update_environment(prefix):
    join = os.path.join

    env = read_env_d(join(prefix, "etc/env.d"))
    update_file(join(prefix, "etc/profile.env"), generate_profile_env(env))
    update_file(join(prefix, "etc/csh.env"), generate_profile_env(env, 'setenv %s %s\n'))

#
# Command line driver
#


def usage():
    print("update-environment [--destdir <prefix>]")


def main(argv):
    prefix = "/"

    try:
        opts, args = getopt.gnu_getopt(argv, "h", ["help", "destdir=", "live"])
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        if o in "--destdir":
            prefix = a

    update_environment(prefix)


if __name__ == "__main__":
    main(sys.argv[1:])
