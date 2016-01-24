Network Configuration Generator
===============================

This Web application is a simple configuration generator for network equipment like Routers and Switches.

It is based on python3 and the [Flask microframework](http://flask.pocoo.org). If you like to know more about the Use 
Case and development of this Web service, take a look on the associated blog series 
"[How to build your own configuration generator](https://codingnetworker.com/2015/12/network-configuration-generator/)". 
 
**This Web service is currently in development, therefore no update path is maintained.**

## run the Web service

**Please Note: All setup scripts assume that this Web service is the only service running on the server.**

There are multiple ways to run this Web service:
 
  * on a Linux server (tested with Ubuntu 14.04)
  * as a Vagrant VM (see Vagrantfile)
  * local on your system (currently only tested with Mac OS X)
  
The configuration of the Web service depends on the `APP_SETTINGS` environment variable. The following values are possible.

| Configuration value           | used for   |
| ----------------------------- | ---------- |
| `config.DefaultConfig`        | Configuration using SQLite                 |
| `config.ProductionConfig`     | Configuration for a production environment |
| `config.TestConfig`           | Configuration for unit-tests               |
| `config.LiveServerTestConfig` | Configuration for selenium-tests           |

If the `APP_SETTINGS` variable is not set, the `DefaultConfig` is used. Furthermore, the `SECRET_KEY` variable is used 
to define a key value for the CSRF protection. Within a production environment, this key is dynamically created during 
the setup of a production environment.

### on a Ubuntu Linux machine

To setup the Web service on a Ubuntu machine, use the following commands:

```Shell
$ git clone https://github.com/hoelsner/network-config-generator.git network_config_generator
$ cd network_config_generator
$ ./setup.sh
```

Follow the instructions from the setup script.

### with Vagrant

To setup the Web service using [Vagrant](vagrantup.com), use the following commands:

```Shell
$ git clone https://github.com/hoelsner/network-config-generator.git network_config_generator
$ cd network_config_generator
$ vagrant up
```

Follow the instructions from the setup script.

### on your local machine

To run an instance on your local machine (for demo or testing), you need the following steps:
 
#### 1. clone the repository

```Shell
$ git clone https://github.com/hoelsner/network-config-generator.git network_config_generator
$ cd network_config_generator
```

#### 2. create a virtualenv and install python dependencies

```Shell
$ virtualenv -p /usr/bin/python3 venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

#### 3. run the local server

```Shell
(venv) $ python3 run_local.py
Initialize database...
Start the Network Configuration Generator on port 5000...
```

## license

See the [license](LICENSE.md) file for license rights and limitations (MIT).

## development and testing

To enable the debug mode of the Web service, set the `DEBUG_MODE` environment variable to `1`. This will also enable 
the logging to the console.

The `tests` directory contains all unit and functional test-cases for the Web service. Use the following command to run 
all test cases bundled with this application (assuming you already created a virtualenv and installed the dependencies 
from the `requirements.txt` and `requirements_text.txt`):

```Shell
(venv) $ python3 -m unittest tests.run_tests_all
```