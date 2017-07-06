
Kong Command Line Client
===========

A command line client for API Gateway - [Kong][kong-url]. The default Kong APIs are in HTTP RESTful style. Normally you need to use `curl` to access it. `kong-cli` make this easier.

`kong-cli` is compatible with Kong 0.10.x.

## Installation

`sudo python setup.py install`

or

`make`


## Configuration

`kong-cli` need to know the Kong host url. It use local Kong admin API url `http://localhost:8001` by default. You can set it by configuration file. The default configuration file is `~/.kong`. You can find a template from `kong.conf`. Copy it to ~/.kong or use `kong-cli --conf kong.conf` to use it.


## Usage

	$ kong-cli
	Usage: kong-cli [OPTIONS] COMMAND [ARGS]...
	
	Options:
	  --conf TEXT
	  --debug / --no-debug
	  --help                Show this message and exit.
	
	Commands:
	  api
	  config
	  consumer
	  key-auth
	  plugin
	  status


## Demo

[![asciicast](https://asciinema.org/a/122418.png)](https://asciinema.org/a/122418)

## Author

Simon / Jinyu LIU <simon.jinyu.liu#gmail.com>

## License
```
Copyright 2017 Jinyu LIU

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

[kong-url]: https://getkong.org/
