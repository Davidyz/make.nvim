# make.nvim

A wrapper of the built in `:make` command.  
Instead of only looking for `Makefile` in the current directory, it also tries
to find `Makefile` in all the parent directories. This allows running `make`
jobs in subdirectories of the repository.


## Usage
`:Make {make_target}`
You may also pass other argument to this command. For example:
```bash
:Make -j2
```

## Requirement
Python3 support for neovim.

## Installation
> This plugin uses the Python api from `neovim` and has only been tested on
> neovim.

Packer.nvim: 
```lua
use 'Davidyz/make.nvim'
```
