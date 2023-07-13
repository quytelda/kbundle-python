#!/usr/bin/env python3

import bundle as B
import sys
import os

def index_of(x, xs):
    try:
        return xs.index(x)
    except ValueError:
        return -1

def main(args):
    bundle_root = os.curdir

    i = index_of("-r", args)
    if i >= 0 and (i+1) < len(args):
        args.pop(i)
        bundle_root = args.pop(i)

    if len(args) <= 0:
        print("Not enough arguments!", file=sys.stderr)
        print("Usage: kbundle [-r <DIR>] <COMMAND> [ARG]...")
        return 1

    command = args.pop(0)
    bundle = B.Bundle(bundle_root)
    if not bundle.load():
        print("Failed to load bundle.", file=sys.stderr)
        return 2

    ok = False
    if command == "update":
        ok = bundle.update_manifest()
    elif command == "build":
        ok = bundle.build(args[0])
    elif command == "add-tag":
        ok = bundle.add_tag(args[1], args[0])
    elif command == "remove-tag":
        ok = bundle.remove_tag(args[1], args[0])
    else:
        print("Unrecognized command or not enough arguments.", file=sys.stderr)

    return 0 if ok else 3

if __name__ == "__main__":
    result = main(sys.argv[1:])
    exit(result)
