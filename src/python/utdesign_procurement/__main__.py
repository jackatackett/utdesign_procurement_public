#!/usr/bin/env python3

import cherrypy, os

from server import Root
from emailer import fork_emailer

def main():

    # setup the email server
    # TODO prompt for these credentials!
    email_process, email_queue = fork_emailer(email_user='noreplygettit@gmail.com',
                         email_password='0ddrun knows all',
                         email_inwardly=True)

    email_process.start()

    #configure the cherrypy server
    cherrypy.Application.wwwDir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.path.join('..', '..', 'www'))

    server_config = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'etc', 'server.conf'))

    cherrypy.tree.mount(
        Root(email_queue, show_debugger=True),
        '/',
        config=server_config)

    cherrypy.engine.start()
    input()
    cherrypy.engine.stop()
    email_queue.put(('die', dict()))
    email_process.join()

if __name__ == '__main__':
    main()
