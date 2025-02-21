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


### Module executed as expected when run as `pyinfra <xxx> src/pysetmeup/zzz.py`

If you have defined a `depploy` function, decorated by the `pyinfra.api.deploy` decorator, to execute it automatically, use this approach:

```python
# Add this line in the end
if __name__ in {"builtins", "__main__"}:
    deploy()
```

## Debugging with `uvx`

Although `uvx` is a great way to debug, bear in mind that your changes may not be
reflected when editing files. A simple workaround is to use `--no-cache`, for example:

```shell
uvx --no-cache --with . pyinfra
```
