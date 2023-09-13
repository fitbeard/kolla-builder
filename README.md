# Tools for automatic Openstack Kolla image building

Script `kolla-builder.py` automatically fetches corresponding commits of desired Openstack projects
and generates `kolla-build.conf` for later use with in `kolla` toolset.

The idea here is to control building process and pin versions if needed.

To understand whole process please take a look how github workflows are configured for this repository
and examples in open/closed pull requests.

## Contributing

You'll need to make sure that you have [`pre-commit`](https://pre-commit.com)
setup and installed in your environment by running these commands:

```console
pre-commit install --hook-type commit-msg
````
