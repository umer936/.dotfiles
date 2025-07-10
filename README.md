# .dotfiles

This repo contains my personal configuration files (.dotfiles) for Linux. I use [GNU Stow](https://www.gnu.org/software/stow/) to manage them by creating symbolic links to the correct locations.

Example:
`~/.dotfiles/bash/.bashrc` → `~/.bashrc`

---

## Install Stow

```sh
# Debian/Ubuntu
sudo apt install stow

# macOS
brew install stow

# Fedora
sudo dnf install stow
```

If no package manager, download manually:

```sh
wget http://ftp.gnu.org/gnu/stow/stow-latest.tar.gz
```

> ⚠️ Windows not supported (should I?). [See this PowerShell port](https://github.com/mattialancellotti/Stow/blob/master/Main.ps1)

---

## Usage

### 1. Move files into your dotfiles repo

```sh
mkdir -p ~/.dotfiles/path/to/file/
mv ~/path/to/file ~/.dotfiles/path/to/file/
```

### 2. Create the symlinks

```sh
stow -d ~/.dotfiles -t ~ path/to/file/
```

* `-d`: directory with dotfiles
* `-t`: target directory (usually `~`)
* `path/to/file/`: the folder inside your dotfiles repo to link

---

## References

* https://www.gnu.org/software/stow/
* https://www.gnu.org/software/stow/manual/stow.html
* https://systemcrafters.net/managing-your-dotfiles/using-gnu-stow/
