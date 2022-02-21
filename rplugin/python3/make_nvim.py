from typing import List, Optional
import neovim
import os
import pathlib


@neovim.plugin
class Main:
    def __init__(self, vim):
        self.vim: neovim.Nvim = vim
        self.__make_path = self.find_make()
        with open("rplugin/python3/make_opts.txt") as fin:
            self.__opts = [
                i[:-1] if i[-1] == "\n" else i for i in fin.readlines()
            ]

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

        options = []
        if currentWord != "" and currentWord[0] == "-":
            options = [i for i in self.__opts if currentWord in i]
        valid_targets = [i for i in self.get_make_targets() if currentWord in i]
        if valid_targets:
            return options + valid_targets
        else:
            return options + self.get_make_targets()

    @neovim.command(
        "Make",
        range="",
        nargs="*",
        sync=True,
        complete="customlist,MakeCompletion",
    )
    def make(self, args: list[str], range: list[list[int]]):
        original_dir = os.getcwd()
        make_dir = self.find_make()
        self.vim.command(f"cd {make_dir}")
        command = f'make {" ".join(args)}'
        self.vim.command(f'echo "{command}"')
        self.vim.command(command)
        self.vim.command(f"cd {original_dir}")

    def find_make(self) -> Optional[str]:
        current_dir = os.getcwd()
        while current_dir:
            if "Makefile" in os.listdir(current_dir):
                return current_dir
            elif current_dir == str(pathlib.Path(current_dir).parent):
                return None
            current_dir = str(pathlib.Path(current_dir).parent)
        return None

    def get_make_targets(self) -> List[str]:
        make_dir = self.find_make()
        if make_dir is None:
            return []
        with open(os.path.join(make_dir, "Makefile")) as fin:
            content = [
                i.replace("\n", "")
                for i in fin.readlines()
                if i[0] != " " and i[0] != "\t"
            ]
        return [x.split(":")[0] for x in content]


if __name__ == "__main__":
    pass
