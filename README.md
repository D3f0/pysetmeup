# Dev Machine Deploy Scripts

Setup fish shell, zoxide, tmux + scritps, Docker, etc.

It has some specific configurations for RedHat hosts like EPEL repo (and Docker)

## Experimental features

### Connector

A lima connector, to use VMs created by limactl.

## Similar projects

- https://github.com/activatedgeek/dotfiles/
- https://github.com/zsxoff/archlinux-pyinfra


## Common issues


### 💥 No such module 

```console
-> pyinfra error: No such module: pyinfra.operations.pysetmeup.deploys.rclone
```

**Solution:** `uv run pyinfra INVETORY pysetmeup.deploys.rclone`
