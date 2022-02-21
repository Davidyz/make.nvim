from typing import List, Optional
import neovim
import os
import pathlib


@neovim.plugin
class Main:
    def __init__(self, vim: neovim.Nvim):
        self.__RUNTIME_PATH: str = os.path.sep.join(
            __file__.split(os.path.sep)[:-1]
        )
        self.vim = vim
        self.__make_path = self.find_make()
        with open(os.path.join(self.__RUNTIME_PATH, "make_opts.txt")) as fin:
            self.__opts = [i.strip() for i in fin.readlines()]

    def find_current_word(self, cmdline: str, cursor: int) -> str:
        head, tail = cursor, cursor
        while head > 4 and cmdline[head - 1] != " ":
            head -= 1
        while tail < len(cmdline) and cmdline[tail] != " ":
            tail += 1
        if tail > head:
            return cmdline[head:tail]
        return ""

    @neovim.function("MakeCompletion", sync=True)
    def make_completion(self, args):
        argLead, cmdline, cursorPos = args
        currentWord = self.find_current_word(cmdline, cursorPos - 1)
        self.vim.api.command(f'echo "{args}"')

        if argLead == "":
            return self.get_make_targets()
        options = []
        for source in (self.get_make_targets(), self.__opts):
            for i in source:
                if argLead == i[: len(argLead)]:
                    options.append(i)
        if options:
            return options
        else:
            return self.get_make_targets()

    @neovim.command(
        "Make",
        range="",
        nargs="*",
        sync=True,
        complete="customlist,MakeCompletion",
    )
    def make(self, args: List[str], range: List[List[int]]):
        original_dir = os.getcwd()
        make_dir = self.find_make()
        if make_dir is None:
            self.vim.command("echo 'No Makefile can be found.'")
            return
        self.vim.command(f"cd {make_dir}")
        command = f'make {" ".join(args)}'
        self.vim.command(f'echo "{command}"')
        self.vim.command(command)
        self.vim.command(f"cd {original_dir}")

    @neovim.function("MakeRootCompletion", sync=True)
    def make_root_completion(self, args):
        argLead, cmdline, cursorPos = args
        currentWord = self.find_current_word(cmdline, cursorPos - 1)
        self.vim.api.command(f'echo "{args}"')

        if argLead == "":
            return self.get_make_targets(top=True)
        options = []
        for source in (self.get_make_targets(top=True), self.__opts):
            for i in source:
                if argLead == i[: len(argLead)]:
                    options.append(i)
        if options:
            return options
        else:
            return self.get_make_targets(top=True)

    @neovim.command(
        "MakeRoot",
        range="",
        nargs="*",
        sync=True,
        complete="customlist,MakeRootCompletion",
    )
    def make_root(self, args: List[str], range: List[List[int]]):
        original_dir = os.getcwd()
        make_dir = self.find_make(top=True)
        if make_dir is None:
            self.vim.command("echo 'No Makefile can be found.'")
            return
        self.vim.command(f"cd {make_dir}")
        command = f'make {" ".join(args)}'
        self.vim.command(f'echo "{command}"')
        self.vim.command(command)
        self.vim.command(f"cd {original_dir}")

    def find_make(self, top=False) -> Optional[str]:
        current_dir = os.getcwd()
        make_dir = None
        while current_dir:
            if "Makefile" in os.listdir(current_dir):
                make_dir = current_dir
                if not top:
                    return (
                        None
                        if current_dir is None
                        else os.path.realpath(current_dir)
                    )
            elif current_dir == str(pathlib.Path(current_dir).parent):
                break
            current_dir = str(pathlib.Path(current_dir).parent)
        return None if make_dir is None else os.path.realpath(make_dir)

    def get_make_targets(self, top=False) -> List[str]:
        make_dir = self.find_make(top)
        if make_dir is None:
            return []
        with open(os.path.join(make_dir, "Makefile")) as fin:
            content = [
                i.strip()
                for i in fin.readlines()
                if i[0] != " " and i[0] != "\t" and i.strip().endswith(":")
            ]
        return [x.split(":")[0] for x in content]


if __name__ == "__main__":
    pass
