import sys

def main():
    args = sys.argv[1:]
    print(sys.argv)
    print(args)
    if args[0] == 'use':
        return 1
    return 0

sys.exit(main())
