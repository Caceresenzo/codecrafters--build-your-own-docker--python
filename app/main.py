import os
import sys


def main():
    image = sys.argv[2]
    argv = sys.argv[3:]

    os.execv(argv[0], argv)


if __name__ == "__main__":
    main()
