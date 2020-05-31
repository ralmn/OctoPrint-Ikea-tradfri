# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Copyright (C) 2015 The OctoPrint Project - Released under terms of the AGPLv3 License"


def commands(cli_group, pass_octoprint_ctx, *args, **kwargs):
    import click
    from octoprint.cli.client import create_client, client_options

    @click.command()
    @client_options
    def turnOn(apikey, host, port, httpuser, httppass, https, prefix):
        click.echo('On')
        client = create_client(settings=cli_group.settings,
            apikey=apikey,
            host=host,
            port=port,
            httpuser=httpuser,
            httppass=httppass,
            https=https,
            prefix=prefix)

        data = dict(
            command="turnOn"
        )
        client.post_json('/api/plugin/ikea_tradfri', data=data)
        

    @click.command()
    @client_options
    def turnOff(apikey, host, port, httpuser, httppass, https, prefix):
        click.echo('off')
        client = create_client(settings=cli_group.settings,
            apikey=apikey,
            host=host,
            port=port,
            httpuser=httpuser,
            httppass=httppass,
            https=https,
            prefix=prefix)

        data = dict(
            command="turnOff"
        )
        client.post_json('api/plugin/ikea_tradfri', data=data)

    return [turnOn, turnOff]
