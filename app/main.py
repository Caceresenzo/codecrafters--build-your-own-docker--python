import os
import sys


def main():
    image = sys.argv[2]
    argv = sys.argv[3:]

    pid = os.fork()
    if not pid:
        os.execv(argv[0], argv)

    _, status = os.waitpid(pid, 0)
    exit_code = os.WEXITSTATUS(status)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
