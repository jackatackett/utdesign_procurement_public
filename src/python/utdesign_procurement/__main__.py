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
                         email_inwardly=True,               #set to True for testing; set to False for production to send emails to all
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

    # Uncomment this line for emails
    email_handler.start()
    cherrypy.engine.start()

    # so windows users can exit gracefully
    windows = not os.path.exists('./.notwindows')

    if windows:
        input()
        cherrypy.engine.stop()
    else: #linux
        cherrypy.engine.block()

    email_handler.die()

if __name__ == '__main__':
    main()
