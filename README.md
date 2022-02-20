# make.nvim

A more powerful Make command compared to the original `:make` command.  
Instead of only looking for `Makefile` in the current directory, it also tries
to find `Makefile` in all the parent directories. This allows running `make`
jobs in subdirectories of the repository.


## Usage
`:Make {make_target}`

## Requirement
Python3 support for neovim.
