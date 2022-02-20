import neovim
import os
import pathlib


@neovim.plugin
class Main:
    def __init__(self, vim):
        self.vim: neovim.Nvim = vim

    @neovim.command("Make", range="", nargs="*", sync=True)
    def make(self, args: list[str], range):
        original_dir = os.getcwd()
        current_dir = os.getcwd()
        while current_dir:
            if "Makefile" in os.listdir(current_dir):
                break
            elif current_dir == str(pathlib.Path(current_dir).parent):
                self.vim.command("echo 'No Makefile is found.'")
                return
            current_dir = str(pathlib.Path(current_dir).parent)

        self.vim.command(f"cd {current_dir}")
        command = f'make {" ".join(args)}'
        self.vim.command(f'echo "{command}"')
        self.vim.command(command)
        self.vim.command(f"cd {original_dir}")


if __name__ == "__main__":
    pass
