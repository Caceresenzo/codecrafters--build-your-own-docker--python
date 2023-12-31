import os
import sys
import tempfile
import shutil

from . import libc, hub


def main():
    image = sys.argv[2]
    argv = sys.argv[3:]

    program_path = argv[0]

    with tempfile.TemporaryDirectory() as root_path:
        hub.pull(image, root_path)

        program_dir = os.path.join(
            root_path,
            "./" + os.path.dirname(program_path)
        )

        if os.path.exists(program_dir) and not os.path.exists(program_dir):
            os.makedirs(program_dir, exist_ok=True)
            shutil.copy2(program_path, program_dir)

        libc.unshare(libc.CLONE_NEWPID)

        pid = os.fork()
        if not pid:
            os.chroot(root_path)
            os.execvp(argv[0], argv)

        _, status = os.waitpid(pid, 0)
        exit_code = os.WEXITSTATUS(status)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
