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
        with open(os.path.join(self.__RUNTIME_PATH, "make_opts.txt")) as fin:
            self.__opts = [i.strip() for i in fin.readlines()]

    @neovim.function("MakeCompletion", sync=True)
    def make_completion(self, args):
        """
        Auto-completion function for :Make.
        """
        return self.run_completion(args, self.find_make(False))

    @neovim.command(
        "Make",
        range="",
        nargs="*",
        sync=True,
        complete="customlist,MakeCompletion",
    )
    def make(self, args: List[str], range: List[List[int]]):
        """
        Run make command from the Makefile in the closest parent directory.
        """
        self.run_make(self.find_make(top=False), args)

    @neovim.function("MakeRootCompletion", sync=True)
    def make_root_completion(self, args):
        """
        Auto-completion function for :MakeRoot.
        """
        return self.run_completion(args, self.find_make(top=True))

    @neovim.command(
        "MakeRoot",
        range="",
        nargs="*",
        sync=True,
        complete="customlist,MakeRootCompletion",
    )
    def make_root(self, args: List[str], range: List[List[int]]):
        """
        Run make command from the Makefile in the top-most parent directory.
        Useful when there are multiple Makefiles in a project.
        """
        self.run_make(self.find_make(top=True), args)

    def run_make(self, make_dir: Optional[str], args: List[str]) -> None:
        """
        Run the Makefile in the given directory.
        """
        if make_dir is None:
            self.vim.command("echo 'No Makefile can be found.'")
            return

        self.vim.command("tabnew")
        original_dir = os.getcwd()
        self.vim.command(f"cd {make_dir}")
        command = f'make {" ".join(args)}'
        self.vim.command(f'echo "{command}"')
        self.vim.command(f"ter {command}")
        self.vim.command(f"cd {original_dir}")

    def run_completion(self, args: List, make_dir: Optional[str]) -> List[str]:
        """
        Find all matching words for the given input.
        """
        argLead = args[0]
        self.vim.api.command(f'echo "{args}"')

        if argLead == "":
            return self.get_make_targets(make_dir)
        options = []
        for source in (self.get_make_targets(make_dir), self.__opts):
            for i in source:
                if argLead in i:
                    options.append(i)
        if options:
            return options
        else:
            return self.get_make_targets(make_dir)

    def find_make(self, top: bool = False) -> Optional[str]:
        """
        Find the directory containing the suitable Makefile.
        top: if True, return the top-most directory for :MakeRoot.
            Otherwise return the closest parent directory containing Makefile."""
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

    def get_make_targets(self, make_dir: Optional[str]) -> List[str]:
        """
        Parse a Makefile to get all the make targets for completion function.
        """
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
