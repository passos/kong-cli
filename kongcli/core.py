#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import hashlib
import click
import requests
import simplejson as json
import logging
import ConfigParser

import utils


def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=2 * ' ')


def cleanup_params(data, empty_string=False):
    for k, v in data.items():
        if not isinstance(v, (unicode, str, int)) or (empty_string and v == ""):
            data.pop(k)
    data.pop('kong', None)
    return data


def error(message):
    raise RuntimeError(message)


def handle_json_response(r, output=True):
    if r.ok:
        result = r.json()
        if output:
            print pretty_json(result)
        return result
    else:
        print r.text


def handle_plain_response(r, output=False):
    if output:
        print r.text
    return r.text


class Kong(object):
    def __init__(self, conf=None, debug=False):
        self.conf = os.path.abspath(conf or '.')
        self.debug = debug
        self.form_header = {'Content-type': 'application/x-www-form-urlencoded'}

        config = ConfigParser.RawConfigParser()
        config.read(self.conf)
        #self.config = config

        if config.has_option("config", "host"):
            self.host = config.get("config", "host")
        else:
            self.host = "http://127.0.0.1:8001"

        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def get_api_url(self, path):
        return "%s%s" % (self.host, path)

    def get(self, path, params=None):
        url = self.get_api_url(path)
        logging.debug("params: %s" % (pretty_json(params)))
        r = requests.get(url, params)
        if r.ok:
            return r
        else:
            error("GET %s with params: %s, Error %s: %s" % (url, pretty_json(params), r.status_code, r.text))

    def put(self, path, json=None, data=''):
        url = self.get_api_url(path)
        logging.debug("put data: %s" % (pretty_json(data)))
        if json:
            r = requests.put(url, json=json)
        else:
            r = requests.put(url, data=data)
        if r.ok:
            return r
        else:
            error("PUT %s with data: %s, Error %s: %s" % (url, pretty_json(data), r.status_code, r.text))

    def post(self, path, json=None, data=''):
        url = self.get_api_url(path)
        logging.debug("post data: %s" % (pretty_json(data)))
        if json:
            r = requests.post(url, json=json)
        else:
            r = requests.post(url, data=data, headers=self.form_header)
        if r.ok:
            return r
        else:
            error("POST %s with data: %s, Error %s: %s" % (url, pretty_json(data), r.status_code, r.text))

    def patch(self, path, json=None, data=''):
        url = self.get_api_url(path)
        logging.debug("patch data: %s" % (pretty_json(data)))
        if json:
            r = requests.patch(url, json=json)
        else:
            r = requests.patch(url, data=data, headers=self.form_header)
        if r.ok:
            return r
        else:
            error("PATCH %s with data: %s, Error %s: %s" % (url, pretty_json(data), r.status_code, r.text))

    def delete(self, path):
        url = self.get_api_url(path)
        r = requests.delete(url)
        if r.ok:
            return r
        else:
            error("DELETE %s Error %s: %s" % (url, r.status_code, r.text))




@click.group(help="Kong configuration")
@click.option('--conf', envvar='KONG_CONF', default=os.path.expanduser("~/.kong"))
@click.option('--debug/--no-debug', envvar='KONG_DEBUG', default=False)
@click.pass_context
def cli(ctx, conf, debug):
    ctx.obj = Kong(conf, debug)


@cli.command()
@click.pass_obj
def config(kong):
    print pretty_json(vars(kong))


@cli.command()
@click.pass_obj
def status(kong):
    r = kong.get("/status")
    print pretty_json(r.json())



@cli.group()
@click.pass_obj
def api(kong):
    logging.debug("apis")


@api.command("list")
@click.option('--id', help="a filter on the list based on the api `id` field")
@click.option('--name', help="a filter on the list based on the api `name` field")
@click.option('--upstream-url', help="a filter on the list based on the api `upstream_url` field")
@click.option('--retries', help="a filter on the list based on the api `retries` field")
@click.option('--size', help="a filter on the list based on the api `size` field")
@click.option('--offset', help="a filter on the list based on the api `offset` field")
@click.pass_obj
def api_list(kong, id, name, upstream_url, retries, size, offset):
    params = cleanup_params(vars())
    r = kong.get("/apis/", params=params)
    return handle_json_response(r)



@api.command("get")
@click.argument('name')
@click.pass_obj
def api_get(kong, name):
    params = cleanup_params(vars())
    r = kong.get("/apis/%s" % name)
    return handle_json_response(r)


@api.command("add")
@click.argument('name')
@click.option('--hosts', prompt='hosts', default="example.com", help="A comma-separated list of domain names that point to your API")
@click.option('--uris', prompt='uris', default="", help="A comma-separated list of URIs prefixes that point to your API.")
@click.option('--methods', prompt='methods', default="GET,PUT,POST,DELETE", help="A comma-separated list of HTTP methods that point to your API.")
@click.option('--upstream-url', prompt='upstream url', default="https://example.com", help="The base target URL that points to your API server. ")
@click.option('--strip-uri', help="When matching an API via one of the uris prefixes, strip that matching prefix from the upstream URI to be requested. ")
@click.option('--preserve-host', help="When matching an API via one of the hosts domain names, make sure the request Host header is forwarded to the upstream service.")
@click.option('--retries', help="The number of retries to execute upon failure to proxy. ")
@click.option('--upstream-connect-timeout', help="The timeout in milliseconds for establishing a connection to your upstream service. ")
@click.option('--upstream-send-timeout', help="The timeout in milliseconds between two successive write operations for transmitting a request to your upstream service")
@click.option('--upstream-read-timeout', help="The timeout in milliseconds between two successive read operations for transmitting a request to your upstream service")
@click.option('--https-only', help="To be enabled if you wish to only serve an API through HTTPS")
@click.option('--http-if-terminated', help="Consider the X-Forwarded-Proto header when enforcing HTTPS only traffic")
@click.pass_obj
def api_add(kong, name, hosts, uris, methods, upstream_url, strip_uri, preserve_host, retries,
    upstream_connect_timeout, upstream_send_timeout, upstream_read_timeout, https_only,
    http_if_terminated):
    data = cleanup_params(vars(), True)
    r = kong.post("/apis/", data=data)
    return handle_json_response(r)


@api.command("update")
@click.argument('name')
@click.option('--hosts', help="A comma-separated list of domain names that point to your API")
@click.option('--uris', help="A comma-separated list of URIs prefixes that point to your API.")
@click.option('--methods', help="A comma-separated list of HTTP methods that point to your API.")
@click.option('--upstream-url', help="The base target URL that points to your API server. ")
@click.option('--strip-uri', help="When matching an API via one of the uris prefixes, strip that matching prefix from the upstream URI to be requested. ")
@click.option('--preserve-host', help="When matching an API via one of the hosts domain names, make sure the request Host header is forwarded to the upstream service.")
@click.option('--retries', help="The number of retries to execute upon failure to proxy. ")
@click.option('--upstream-connect-timeout', help="The timeout in milliseconds for establishing a connection to your upstream service. ")
@click.option('--upstream-send-timeout', help="The timeout in milliseconds between two successive write operations for transmitting a request to your upstream service")
@click.option('--upstream-read-timeout', help="The timeout in milliseconds between two successive read operations for transmitting a request to your upstream service")
@click.option('--https-only', help="To be enabled if you wish to only serve an API through HTTPS")
@click.option('--http-if-terminated', help="Consider the X-Forwarded-Proto header when enforcing HTTPS only traffic")
@click.pass_obj
def api_update(kong, name, hosts, uris, methods, upstream_url, strip_uri, preserve_host, retries,
    upstream_connect_timeout, upstream_send_timeout, upstream_read_timeout, https_only,
    http_if_terminated):
    data = cleanup_params(vars(), False)
    r = kong.patch("/apis/%s" % (name), data=data)
    return handle_json_response(r)


@api.command("delete")
@click.argument('name')
@click.pass_obj
def api_delete(kong, name):
    r = kong.delete("/apis/%s" % (name))
    return handle_plain_response(r, False)


@cli.group()
@click.pass_obj
def consumer(kong):
    logging.debug("consumers")


@consumer.command("list")
@click.option('--id', help="a filter on the list based on the customer `id` field")
@click.option('--custom-id', help="a filter on the list based on the customer `custom_id` field")
@click.option('--username', help="a filter on the list based on the customer `username` field")
@click.option('--size', help="a filter on the list based on the customer `size` field")
@click.option('--offset', help="a filter on the list based on the customer `offset` field")
@click.pass_obj
def consumer_list(kong, id, custom_id, username, size, offset):
    params = cleanup_params(vars())
    r = kong.get("/consumers/", params)
    return handle_json_response(r)


@consumer.command("get")
@click.argument('username')
@click.option('--show-plugins/--no-plugins', default=False, help="show consumer related plugins or not")
@click.pass_obj
def consumer_get(kong, username, show_plugins=False):
    r = kong.get("/consumers/%s" % username)
    if r.ok:
        result = r.json()
        if show_plugins:
            result['plugins'] = get_consumer_plugins(kong, result['id'])
        print pretty_json(result)
        return result
    else:
        print r.text


@consumer.command("add")
@click.argument('username')
@click.option('--custom-id', help="Field for storing an existing ID for the consumer, useful for mapping Kong with users in your existing database")
@click.pass_obj
def consumer_add(kong, username, custom_id):
    data = cleanup_params(vars(), True)
    r = kong.post("/consumers/", data=data)
    return handle_json_response(r)


@consumer.command("update")
@click.argument('username')
@click.option('--custom-id', help="Field for storing an existing ID for the consumer, useful for mapping Kong with users in your existing database")
@click.pass_obj
def consumer_update(kong, username, custom_id):
    data = cleanup_params(vars(), False)
    r = kong.patch("/consumers/%s" % (username), data=data)
    return handle_json_response(r)


@consumer.command("delete")
@click.argument('username')
@click.pass_obj
def consumer_delete(kong, username):
    r = kong.delete("/consumers/%s" % (username))
    return handle_plain_response(r, False)


def get_consumer_plugins(kong, consumer_id):
    r = kong.get("/plugins/")
    data = r.json()['data']
    result = []
    for plugin in data:
        if 'consumer_id' in plugin:
            if plugin['consumer_id'] == consumer_id:
                result.append(plugin)
        else:
            result.append(plugin)

    return result



@cli.group()
@click.pass_obj
def plugin(kong):
    print "plugins"


@plugin.command("list")
@click.argument('api', required=False)
@click.option('--id', help="a filter on the list based on the plugin `id` field")
@click.option('--name', help="a filter on the list based on the plugin `name` field")
@click.option('--api-id', help="a filter on the list based on the plugin `api_id` field")
@click.option('--consumer-id', help="a filter on the list based on the plugin `custom_id` field")
@click.option('--size', help="a filter on the list based on the plugin `size` field")
@click.option('--offset', help="a filter on the list based on the plugin `offset` field")
@click.pass_obj
def plugin_list(kong, api, id, name, api_id, consumer_id, size, offset):
    params = cleanup_params(vars())
    if api:
        params.pop("api")
        r = kong.get("/apis/%s/plugins/" % api, params)
        return handle_json_response(r)
    else:
        r = kong.get("/plugins/", params)
        return handle_json_response(r)


@plugin.command("get")
@click.argument('id')
@click.pass_obj
def plugin_get(kong, id):
    r = kong.get("/plugins/%s" % id)
    return handle_json_response(r)


def make_config(config):
    result = {}
    for item in config:
        result["config.%s" % item[0]] = item[1]
    return result


@plugin.command("add")
@click.argument('name')
@click.option('--api', prompt="API", help="The name or id of the API")
@click.option('--consumer-id', help="The unique identifier of the consumer that overrides the existing settings for this specific consumer on incoming requests.")
@click.option('--config', '-c', type=(unicode, unicode), multiple=True, help="config name and value in `property value` format, example: `--config id 1` means `config.id=1`")
@click.pass_obj
def plugin_add(kong, api, name, consumer_id, config):
    data = cleanup_params(vars(), True)
    data.pop('api')
    data.update(make_config(config))
    r = kong.post("/apis/%s/plugins/" % api, data=data)
    return handle_json_response(r)


@plugin.command("update")
@click.argument('api')
@click.argument('id')
@click.option('--consumer-id', help="The unique identifier of the consumer that overrides the existing settings for this specific consumer on incoming requests.")
@click.option('--config', '-c', type=(unicode, unicode), multiple=True, help="config name and value in `property value` format, example: `--config id 1` means `config.id=1`")
@click.pass_obj
def plugin_update(kong, api, id, consumer_id, config):
    data = cleanup_params(vars(), False)
    data.pop('api')
    data.update(make_config(config))
    r = kong.patch("/apis/%s/plugins/%s" % (api, id), data=data)
    return handle_json_response(r)


@plugin.command("delete")
@click.argument('api')
@click.argument('id')
@click.pass_obj
def plugin_delete(kong, api, id):
    r = kong.delete("/apis/%s/plugins/%s" % (api, id))
    return handle_plain_response(r, False)


@plugin.command("enabled")
@click.pass_obj
def plugin_enabled(kong):
    r = kong.get("/plugins/enabled")
    return handle_json_response(r)


@plugin.command("schema")
@click.argument('name')
@click.pass_obj
def plugin_schema(kong, name):
    r = kong.get("/plugins/schema/%s" % name)
    return handle_json_response(r)




@cli.group("key-auth")
@click.pass_obj
def key_auth(kong):
    logging.debug("key_auth")


@key_auth.command("list")
@click.argument('username')
@click.pass_obj
def key_auth_list(kong, username):
    r = kong.get("/consumers/%s/key-auth" % (username))
    return handle_json_response(r)


@key_auth.command("add")
@click.argument('username')
@click.option('--key', help="You can optionally set your own unique key to authenticate the client. If missing, the plugin will generate one.")
@click.pass_obj
def key_auth_add(kong, username, key):
    data = cleanup_params(vars(), True)
    data.pop('username')
    r = kong.post("/consumers/%s/key-auth" % (username), data=data)
    return handle_json_response(r)


@key_auth.command("delete")
@click.argument('username')
@click.argument('key')
@click.pass_obj
def key_auth_delete(kong, username, key):
    r = kong.delete("/consumers/%s/key-auth/%s" % (username, key))
    return handle_plain_response(r, False)



@cli.group("acl")
@click.pass_obj
def acl(kong):
    logging.debug("acl")


@acl.command("list")
@click.argument('username')
@click.pass_obj
def acl_list(kong, username):
    r = kong.get("/consumers/%s/acls" % (username))
    return handle_json_response(r)


@acl.command("add")
@click.argument('username')
@click.option('--group', prompt="group", help="The arbitrary group name to associate to the consumer.")
@click.pass_obj
def acl_add(kong, username, group):
    r = kong.post("/consumers/%s/acls" % (username), data="group=%s" % group)
    return handle_json_response(r)


@acl.command("update")
@click.argument('username')
@click.argument('group_id')
@click.option('--group', prompt="group", help="The arbitrary group name to associate to the consumer.")
@click.pass_obj
def acl_update(kong, username, group_id, group):
    r = kong.patch("/consumers/%s/acls/%s" % (username, group_id), data="group=%s" % group)
    return handle_json_response(r)


@acl.command("delete")
@click.argument('username')
@click.argument('group_id')
@click.pass_obj
def acl_delete(kong, username, group_id):
    r = kong.delete("/consumers/%s/acls/%s" % (username, group_id))
    return handle_plain_response(r, False)

