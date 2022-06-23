# This is file allows weggli to run against a provided source
# directory, provided through command line arguments, using some common
# test-cases from the README. This could be a useful part of a CI/CD pipeline
# for c/c++ projects

import os
import subprocess
import argparse


def print_help():
    print("weggli-automator 1.0.0")
    print(
        "An automation script to run C/C++ code-bases against common test-cases with weggli"
    )
    print("USAGE:")
    print("     automate.py [FLAGS] <COMMAND> <PATH>")
    print("<COMMANDS>:")
    print(
        "     memcpy              Looks for calls to memcpy that write into a stack-buffer"
    )
    print(
        "     no-return-check     Looks for calls to a function, foo, that don't check the return value"
    )
    print("     sprintf             Looks for potentially vulnerable snprintf() uses")
    print("     wild                Looks for potentially uninitialized pointers")
    print(
        "     weak                Looks for potentially insecure uses of weak pointers"
    )
    print("     iter                Validate iterator")
    print(
        "     stack               Looks for functions that perform writes into a stack-buffer based on a function argument"
    )
    print("<PATH>: the directory or file to analyze")
    print("OPTIONS:")
    print("     -h, --help       Prints help information")


def weggli_installed() -> bool:
    return os.path.exists("~/.cargo/bin/weggli")


def memcpy_stack_write(path: str):
    subprocess.run("weggli '{_ $buf[_]; memcpy($buf,_,_); }' ./{0}".format(path))


def unchecked_return(function_name: str, path: str):
    subprocess.run("weggli '{ strict: {0} (_);}' ./{1}".format(function_name, path))


def uninitialized_pointers(path: str):
    subprocess.run("weggli '{ _* $p; NOT: $p = _; $func(&$p); }' ./{0}".format(path))


def weak_ptr(path: str):
    subprocess.run(
        "weggli --cpp '{$x = _.GetWeakPtr();  DCHECK($x);  $x->_;}' ./{0}".format(path)
    )


def snprintf(path: str):
    subprocess.run(
        "weggli '{$ret = snprintf($b,_,_);$b[$ret] = _;}' ./{0}".format(path)
    )


def iterator_validation(path: str):
    subprocess.run("weggli -X 'DCHECK(_!=_.end());' ./{0}".format(path))


def stack_buffer_writes(path: str):
    subprocess.run(
        "weggli '_ $fn(_ $limit) {_ $buf[_];for (_; $i<$limit; _) {$buf[$i]=_;}}' ./{0}".format(
            path
        )
    )


if __name__ == "__main__":
    # if not weggli_installed():
    #     cross_box = "[\x1b[1;31m\u2717\x1b[0m]"
    #     print(cross_box + " weggli not found")
    #     exit(1)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", "-h", action="store_true")
    parser.add_argument(
        "command",
        nargs="?",
        const="Command was not provided",
        type=str,
        default=None,
        choices=[
            "memcpy",
            "no-return-check",
            "wild",
            "weak",
            "snprintf",
            "iter",
            "stack",
            "all",
        ],
        help="memcpy: Looks for calls to memcpy that write into a stack-buffer\n"
        "no-return-check: Looks for calls to a function, foo, that don't check the return value\n"
        "snprintf: Looks for potentially vulnerable snprintf() uses\n"
        "wild: Looks for potentially uninitialized pointers\n"
        "weak: Looks for potentially insecure uses of weak pointers\n"
        "iter: Validate iterators\n"
        "stack: Looks for functions that perform writes into a stack-buffer based on a function argument\n"
        "all: Run all of the provided functions\n",
    )
    parser.add_argument(
        "path",
        nargs="?",
        const="Project path was not provided",
        type=str,
        default=None,
    )
    args = parser.parse_args()
    print(args)
    if args.command == None:
        print("\033[91m" + "No command provided" + "\033[0m")
        print_help()
        exit(0)
    if not args.command == None and args.path == None:
        print("\033[91m" + "No path provided" + "\033[0m")
        print_help()
        exit(0)
    if os.path.exists(args.path):
        if args.command == "memcpy":
            memcpy_stack_write(args.path)
            exit(1)
        elif args.command == "no-return-check":
            # TODO: Instead of doing it this way, have another optional positional specifically for this command
            function_name = str(input("Enter the function name to check"))
            unchecked_return(function_name, args.path)
            exit(1)
        elif args.command == "wild":
            uninitialized_pointers(args.path)
            exit(1)
        elif args.command == "weak":
            weak_ptr(args.path)
            exit(1)
        elif args.command == "snprintf":
            snprintf(args.path)
            exit(1)
        elif args.command == "iter":
            iterator_validation(args.path)
            exit(1)
        elif args.command == "stack":
            stack_buffer_writes(args.path)
            exit(1)
        elif args.command == "all":
            memcpy_stack_write(args.path)
            # TODO: Instead of doing it this way, have another optional positional specifically for this command
            function_name = str(input("Enter the function name to check"))
            unchecked_return(function_name, args.path)
            uninitialized_pointers(args.path)
            weak_ptr(args.path)
            snprintf(args.path)
            iterator_validation(args.path)
            stack_buffer_writes(args.path)
            exit(1)
    else:
        path = str(args.path)
        print(f"\033[91m" + "The provided path was invalid: " + path + "\033[0m")
    if args.help:
        print_help()
        exit(1)
