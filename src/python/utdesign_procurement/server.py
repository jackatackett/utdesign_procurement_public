#!/usr/bin/env python

import cherrypy
import hashlib
import os
import pymongo as pm
import smtplib

from bson.objectid import ObjectId
from mako.lookup import TemplateLookup
from uuid import uuid4

def authorizedRoles(*acceptableRoles):
    """
    This is a decorator factory which checks the role of a user by their
    session information. If their role is not in the given list of
    authorized roles, then they are denied access. If they aren't logged
    in at all, then they are redirected to the login page.
    """

    def decorator(func):

        def decorated_function(*args, **kwargs):
            role = cherrypy.session.get('role', None)

            cherrypy.log("authorizedRoles called with user role %s and "
                         "roles %s" % (role, acceptableRoles))

            # no role means force a login
            if role is None:
                raise cherrypy.HTTPRedirect('/login')

            # not authorized means raise hell!
            if role not in acceptableRoles:
                raise cherrypy.HTTPError(403)

            # by now, they're surely authorized
            return func(*args, **kwargs)

        return decorated_function

    return decorator

class Root(object):

    def __init__(self, email_user, email_password):
        self.email_user = email_user
        self.email_password = email_password

        templateDir = os.path.join(cherrypy.Application.wwwDir, 'templates')
        cherrypy.log("Template Dir: %s" % templateDir)
        self.templateLookup = TemplateLookup(directories=templateDir)

        client = pm.MongoClient()
        db = client['procurement']
        self.colRequests = db['requests']
        self.colUsers = db['users']
        self.colInvitations = db['invitations']

    # Pages go below. DO EXPOSE THESE

    #no authorization needed for the landing page
    @cherrypy.expose
    def index(self):
        """
        This will redirect users to the proper view

        :return:
        """

        role = cherrypy.session.get('role', None)
        if role is None:
            raise cherrypy.HTTPRedirect('/login')
        elif role == 'student':
            raise cherrypy.HTTPRedirect('/student')
        elif role == 'manager':
            raise cherrypy.HTTPRedirect('/manager')
        elif role == 'admin':
            raise cherrypy.HTTPRedirect('/admin')
        else:
            cherrypy.log("Invalid user role at index. Role: %s" % role)
            raise cherrypy.HTTPError(400, 'Invalid user role')

    #no authorization needed for the login page
    @cherrypy.expose
    def login(self):
        """
        This is the login view.
        """

        role = cherrypy.session.get('role', None)
        if role is not None:
            raise cherrypy.HTTPRedirect('/')

        template = self.templateLookup.get_template('login/LoginApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

    #no authorization needed for the verify page
    @cherrypy.expose
    def verify(self, id):
        """
        This is the account setup page. Here, a user can set their password
        for the first time.
        """

        #TODO make sure the id is actually correct
        template = self.templateLookup.get_template('verify/VerifyApp.html')
        ret = template.render(verifyUUID=id)
        cherrypy.log(str(type(ret)))
        return ret

    @cherrypy.expose
    @authorizedRoles("student")
    def student(self):
        template = self.templateLookup.get_template('student/StudentApp.html')
        ret = template.render()
        return ret

    @cherrypy.expose
    @authorizedRoles("manager")
    def manager(self):
        template = self.templateLookup.get_template('manager/ManagerApp.html')
        ret = template.render()
        return ret

    @cherrypy.expose
    @authorizedRoles("admin")
    def admin(self):
        template = self.templateLookup.get_template('admin/AdminApp.html')
        ret = template.render()
        return ret

    # no authorization needed, because this should be removed in production
    @cherrypy.expose
    def debug(self):
        template = self.templateLookup.get_template('debug/DebugApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

    # TODO Move helper functions to the bottom with the others
    # Helper functions below. DO NOT EXPOSE THESE

    # TODO rename helper functions
    # checks if key value exists and is the right type
    def _helperFunc(self, key, data, dataType, optional=False, default=""):
        if key in data:
            localVar = data[key]
            if isinstance(localVar, dataType):
                return localVar
            else:
                cherrypy.log("Expected %s of type %s. See: %s" % key, dataType, localVar)
                raise cherrypy.HTTPError(400, 'Invalid %s format' % key)
        else:
            if(not optional):
                raise cherrypy.HTTPError(400, 'Missing %s' % key)
            else:
                return default

    # TODO rename helper functions
    # checks if data has valid object ID
    def _helperFunc2(self, data):
        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                return myID
            else:
                raise cherrypy.HTTPError(400, 'Object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

    # TODO rename helper functions
    # is the use of myID valid? (myID is an expected part of the queries)
    # finds document in database and updates it using provided queries
    def _helperFunc3(self, myID, findQuery, updateQuery, updateRule):
            if self.colRequests.find(findQuery).count() > 0:
                self.colRequests.update_one(updateQuery, updateRule, upsert=False)
            else:
                raise cherrypy.HTTPError(400, 'Request matching id and status not found in database')

    # API Functions go below. DO EXPOSE THESE

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementRequest(self):
        """
        Expected input::

            {
                "status": (string),
                "vendor": (string),
                "groupID": (string),
                "URL": (string),
                "justification": (string) optional,
                "additionalInfo": (string) optional
                "items": [
                    {
                    "description": (string),
                    "partNo": (string),
                    "quantity": (string),
                    "unitCost": (string),
                    }
                ]
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')
        
        myRequest = dict()
        
        # set default value of value in dict
        myRequest['status'] = 'pending'

        for key in ("vendor", "URL", "groupID"):
            myRequest[key] = self._helperFunc(key, data, str)

        for key in ("justification", "additionalInfo"):
            myRequest[key] = self._helperFunc(key, data, str, True)

        # items is a list of dicts (each dict is one item)
        # theirItems is a list we receive
        theirItems = self._helperFunc("items", data, list)
        # myItems is the list we are creating and adding to the database
        myItems = []

        for item in theirItems:
            theirDict = self._helperFunc(item, data, dict)
            myDict = dict()
            for key in ("description", "partNo", "quantity", "partCost", "totalCost"):
                myDict[key] = self._helperFunc(key, theirDict, str)
            myItems.append(myDict)

        myRequest["items"] = myItems
            
        # insert the data into the database
        self.colRequests.insert(myRequest)

        #TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student", "manager", "admin")
    def procurementStatuses(self):
        """
        Returns a list of procurement requests matching all provided 
        filters. Currently matches with any combination of vendor, 
        token, groupID, and URL, but also that doesn't work yet.
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = None
            
            
        filters = []
        
        if 'vendor' in data:
            myVendor = data['vendor']
            filters.append(myVendor)
                
        if 'token' in data:
            myToken = data['token']
            filters.append(myToken)
                
        if 'groupID' in data:
            myGroupID = data['groupID']
            filters.append(myGroupID)
            
        if 'URL' in data:
            myURL = data['URL']
            filters.append(myURL)
        
        # currently doesn't make use of filters
        listRequests = list(self.colRequests.find())
        return listRequests

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementCancel(self):
        """
        # TODO add words here
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._helperFunc2(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'$or': [
                    {'status': 'pending'},
                    {'status': 'review'}
                ]}
            ]
        }
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {'$set':
                      {'status': 'cancelled'}
                  }

        self._helperFunc3(myID, findQuery, updateQuery, updateRule)
        
        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("manager", "admin")
    def procurementApprove(self):
        """
        Need to make code pretty,
        check it works.
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._helperFunc2(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': 'pending'}
        ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            '$set':
                {'status': 'approved'}
        }

        self._helperFunc3(myID, findQuery, updateQuery, updateRule)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementReview(self):
        """
        Need to make code pretty, check it works.
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._helperFunc2(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {
                    '$or': [
                        {'status': 'approved'},
                        {'status': 'pending'}
                ]}
        ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': 'review'}
        }

        self._helperFunc3(myID, findQuery, updateQuery, updateRule)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementResubmit(self):
        """
        Need to make code pretty, check it works.
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._helperFunc2(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': 'review'}
        ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': 'pending'}
        }

        self._helperFunc3(myID, findQuery, updateQuery, updateRule)

        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("manager", "admin")
    def procurementReject(self):
        """
        Need to make code pretty, check it works.
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._helperFunc2(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                { '$or': [
                    {'status': 'pending'},
                    {'status': 'approved'}
                ]}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': 'rejected'}
        }

        self._helperFunc3(myID, findQuery, updateQuery, updateRule)

        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userAdd(self):
        """
        I've assumed that every student has:
        a groupID, firstName, lastName, netID, email, and course

        Expected input::

            {
                "groupID": (string),
                "firstName": (string),
                "lastName": (string),
                "netID": (string),
                "email": (string),
                "course": (string),
                "role": (string)
            }

        """

        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myUser = dict()

        # set default value of value in dict
        myUser['status'] = 'current'

        myRole = self._helperFunc("role", data, str)
        if myRole in ("student", "manager", "admin"):
            myUser['role'] = myRole
        else:
            cherrypy.log('Expected role of value "student", "manager", or "admin". See: %s' % myRole)
            raise cherrypy.HTTPError(400, 'Invalid role. Should be "student", "manager", or "admin".')

        for key in ("firstName", "lastName", "groupID", "netID", "email", "course"):
            myUser[key] = self._helperFunc(key, data, str)


        # TODO: make sure the user's email is unique
        # insert the data into the database
        self.colUsers.insert(myUser)

        # create a link (invitation) so the user can set a password
        myInvitation = {
            'uuid': str(uuid4()),
            'expiration': None,
            'email': myUser['email']
        }

        # TODO: email this link to the user
        self.colInvitations.insert(myInvitation)
        cherrypy.log('Created new user. Setup UUID: %s' % myInvitation['uuid'])
        return {'uuid': myInvitation['uuid']}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userEdit(self):
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID): #this takes the id as a string, not an ObjectId -> need to convert it if searching on ObjectId
                # if there exists a user with the given id, change its data and update it
                if self.colUsers.find({'_id': ObjectId(myID)}).count() > 0:
                    cherrypy.log("found ID")
                    data.pop('_id')
                    cherrypy.log("popped id")
                    self.colUsers.update({'_id': ObjectId(myID)}, {"$set": data }) # TODO : doesn't check data is valid
                    cherrypy.log("successful update")
                else:
                    raise cherrypy.HTTPError(400, 'User matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

        # TODO: what do we do with this stuff?
        #~ if '_id' in data:
            #~ myID = data['_id']
            #~ print(myID)
            #~ # if ObjectId.is_valid(myID): #this takes the id as a string, not an ObjectId -> need to convert it if searching on ObjectId
                #~ # if there exists a user with the given id, change its data and update it
            #~ if self.colUsers.find({'_id': myID}).count() > 0:
                #~ cherrypy.log("found ID")
                #~ data.pop('_id')
                #~ cherrypy.log("popped id")
                #~ self.colUsers.update({'_id': myID}, {"$set": data })
                #~ cherrypy.log("successful update")
            #~ else:
                #~ raise cherrypy.HTTPError(400, 'User matching id not found in database')
            #~ # else:
                #~ # raise cherrypy.HTTPError(400, 'object id not valid')
        #~ else:
            #~ raise cherrypy.HTTPError(400, 'data needs object id')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userRemove(self):
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._helperFunc2(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': 'current'}
            ]
        }
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            '$set':
                {'status': 'removed'}
        }

        self._helperFunc3(myID, findQuery, updateQuery, updateRule)

        # TODO send email?

    # don't need to authenticate for this
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def userVerify(self):
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        if not 'uuid' in data:
            raise cherrypy.HTTPError(400, 'Missing UUID')
        elif not 'email' in data:
            raise cherrypy.HTTPError(400, 'Missing email')
        elif not 'password' in data:
            raise cherrypy.HTTPError(400, 'Missing password')

        invitation = self.colInvitations.find_one({'uuid': data['uuid']})
        cherrypy.log("Email: %s. Invitation: %s" % (data['email'], invitation))
        if invitation and invitation.get('email', None) == data['email']:
            salt = Root.generateSalt()
            hash = Root.hashPassword(data['password'], salt)
            self.colUsers.update({
                'email': data['email']
            }, {'$set': {
                'salt': salt,
                'password': hash
            }})
        else:
            raise cherrypy.HTTPError(403, 'Invalid email for this invitation')

    # don't need to authenticate for this
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def userLogin(self):
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # need email and password in data
        if 'email' not in data:
            raise cherrypy.HTTPError(400, 'Missing email')

        if 'password' not in data:
            raise cherrypy.HTTPError(400, 'Missing password')

        # verify password of user
        user = self.colUsers.find_one({'email': data['email']})
        if user and self.verifyPassword(user, data['password']):
            cherrypy.session['email'] = user['email']
            cherrypy.session['role'] = user['role']
            return "<strong> You logged in! </strong>"
        else:
            raise cherrypy.HTTPError(403, 'Invalid email or password.')

    # this function is for debugging for now. If that never changes then
    # TODO remove this function before production if it isn't needed
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def userInfo(self):
        # auth/authenticated is helpful for debugging
        auth = 'role' in cherrypy.session
        ret =  {'authenticated': auth}

        if auth:
            for k in ('role', 'email'):
                ret[k] = cherrypy.session[k]

        # ret is a JSON object containing role and email, and a boolean
        # "authenticated"
        return ret

    @cherrypy.expose
    def userLogout(self):
        cherrypy.lib.sessions.expire()

    # Email Functions

    def emailDo(self, func):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.email_user, self.email_password)
        func(server)
        server.quit()

    def emailSend(self, to, subject, body):
        email_text = '\n'.join((
            'From: %s' % self.email_user,
            'To: %s' % (to if isinstance(to, str) else ', '.join(to)),
            'Subject: %s' % subject,
            '',
            body))

        self.emailDo(
            lambda server: server.sendmail(self.email_user, to, email_text))


    #do not expose this function for any reason
    def verifyPassword(self, user, password):
        # logging password may be security hole; do not include this line in finished product
        # cherrypy.log("verifyPassword %s ::: %s" % (user['password'], Root.hashPassword(password, user['salt'])))

        # user['password'] is hashed password, not plaintext
        if user and 'salt' in user and 'password' in user:
            return user['password'] == Root.hashPassword(password, user['salt'])
        else:
            return False

    #do not expose this function for any reason
    @staticmethod
    def hashPassword(password, salt):
        # use pbkdf2 password hash algorithm, with sha-256 and 100,000 iterations
        # by default, encode encodes string to utf-8
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

    #do not expose this function for any reason
    @staticmethod
    def generateSalt():
        # create 32 byte salt (note: changed from 8)
        # string of random bytes
        # platform-specific (windows uses CryptGenRandom())
        return os.urandom(32)

def main():
    cherrypy.Application.wwwDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
        os.path.join('..', '..', 'www'))

    server_config = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 
        '..', '..', 'etc', 'server.conf'))

    # TODO prompt for these credentials!
    cherrypy.tree.mount(Root('noreplygettit@gmail.com', '0ddrun knows all'),
                        '/', config=server_config)

    cherrypy.engine.start()
    input()
    cherrypy.engine.stop()

if __name__ == '__main__':
    main()
