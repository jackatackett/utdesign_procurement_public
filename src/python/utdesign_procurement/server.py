#!/usr/bin/env python

import cherrypy
import os

from mako.lookup import TemplateLookup

class Root(object):

    def __init__(self):
        templateDir = os.path.join(cherrypy.Application.wwwDir, 'templates')
        cherrypy.log("Template Dir: %s" % templateDir)
        self.templateLookup = TemplateLookup(directories=templateDir)

    @cherrypy.expose
    def index(self):
        template = self.templateLookup.get_template('StudentApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

def main():
    cherrypy.Application.wwwDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../www')

    cherrypy.tree.mount(Root(), '/', config='../../etc/server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    main()