from typing import Iterable, List, Optional
import neovim
import os
import pathlib


@neovim.plugin
class Main:
    def __init__(self, vim):
        self.vim: neovim.Nvim = vim
        self.__make_path = self.find_make()

    @neovim.function("MakeCompletion", sync=True)
    def make_completion(self, args):
        argLead, cmdline, cursorPos = args
        if cmdline[:4] == "Make":
            cmdline = cmdline[4:].strip()

        valid_targets = [i for i in self.get_make_targets() if cmdline in i]
        if valid_targets:
            return valid_targets
        else:
            return self.get_make_targets()

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

    def get_make_targets(self) -> Iterable[str]:
        make_dir = self.find_make()
        if make_dir is None:
            return []
        with open(os.path.join(make_dir, "Makefile")) as fin:
            content = [
                i.replace("\n", "")
                for i in fin.readlines()
                if i[0] != " " and i[0] != "\t"
            ]
        return map(lambda x: x.split(":")[0], content)


if __name__ == "__main__":
    pass
