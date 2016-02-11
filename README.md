# SX Console Lite

SX Console Lite is a fully functional web administration console for Skylable
SX.


## Getting started

### Starting the container
To run your sxconsole-lite instance, simply run `./sxconsole-start.sh`.
It will load the required images and start the containers.

During the first run, you will be asked to provide configuration details for
sxconsole.

By default, SX Console will be running at `https://0.0.0.0:8888/`

### Creating your account
Once the container is up and running, run `./add-admin.sh user@example.com
password` to create your account.
