#!/usr/bin/env python3

import cherrypy, os

from utdesign_procurement.server import Root
from utdesign_procurement.emailer import EmailHandler

def main():

    # setup the email server

    email_template_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'smtp'))

    cherrypy.log('Email template dir: %s' % email_template_dir)

    # TODO prompt for these credentials!
    email_handler = EmailHandler(email_user='noreplygettit@gmail.com',
                         email_password='0ddrun knows all',
                         email_inwardly=True,
                         template_dir=email_template_dir)

    #configure the cherrypy server
    cherrypy.Application.wwwDir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.path.join('..', '..', 'www'))

    server_config = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'etc', 'server.conf'))

    cherrypy.tree.mount(
        Root(email_handler, show_debugger=True),
        '/',
        config=server_config)

    cherrypy.engine.start()
    input()
    cherrypy.engine.stop()
    email_handler.die()

if __name__ == '__main__':
    main()
