#!/usr/bin/env python3

# Copyright 2023 Quytelda Kahja
#
# This file is part of kbundle.
#
# kbundle is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kbundle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kbundle. If not, see <https://www.gnu.org/licenses/>.

import bundle as B
import sys
import os
import argparse

def unpack(bundle, args):
    return bundle.unpack(args.path)

def pack(bundle, args):
    return bundle.pack(args.path)

def update(bundle, args):
    return bundle.update_manifest()

def tag_add(bundle, args):
    return bundle.add_tag(args.path, args.tag)

def tag_del(bundle, args):
    return bundle.remove_tag(args.path, args.tag)

def tag_ls(bundle, args):
    return bundle.print_tags(args.path)

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.set_defaults(load=True)
    parser.add_argument("-r", "--root",
                        default=os.curdir,
                        metavar="DIR",
                        help="the root directory of a bundle tree")

    subparsers = parser.add_subparsers()

    parser_update = subparsers.add_parser("update")
    parser_update.set_defaults(func=update)

    parser_pack   = subparsers.add_parser("pack")
    parser_pack.set_defaults(func=pack)
    parser_pack.add_argument("path")

    parser_unpack = subparsers.add_parser("unpack")
    parser_unpack.set_defaults(func=unpack, load=False)
    parser_unpack.add_argument("path")

    parser_tag = subparsers.add_parser("tag")
    subparsers_tag = parser_tag.add_subparsers()

    parser_tag_ls = subparsers_tag.add_parser("ls")
    parser_tag_ls.set_defaults(func=tag_ls)
    parser_tag_ls.add_argument("path")

    parser_tag_add = subparsers_tag.add_parser("add")
    parser_tag_add.set_defaults(func=tag_add)
    parser_tag_add.add_argument("tag")
    parser_tag_add.add_argument("path")

    parser_tag_remove = subparsers_tag.add_parser("remove")
    parser_tag_remove.set_defaults(func=tag_del)
    parser_tag_remove.add_argument("tag")
    parser_tag_remove.add_argument("path")

    return parser

def main():
    args = get_argument_parser().parse_args()

    bundle = B.Bundle(args.root)
    if args.load and not bundle.load():
        print("Failed to load bundle.", file=sys.stderr)
        return 2

    ok = args.func(bundle, args)
    return 0 if ok else 3

if __name__ == "__main__":
    result = main()
    exit(result)
