#!/usr/bin/env python

import cherrypy
import hashlib
import os
import pymongo as pm

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

    def __init__(self, email_queue, debug=False):

        self.email_queue = email_queue
        self.show_debugger = debug

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

        # TODO check for and alert for expired invitations
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
        #disable this interface in production
        if not self.show_debugger:
            raise cherrypy.HTTPError(404)

        template = self.templateLookup.get_template('debug/DebugApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

    # API Functions go below. DO EXPOSE THESE

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementRequest(self):
        """
        This REST endpoint takes data as an input as uses the data to create
        a procurement request.

        Expected input::

            {
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
                    "totalCost": (number),
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
        
        # set default value of status to pending
        myRequest['status'] = 'pending'

        # mandatory keys
        for key in ("vendor", "URL", "groupID"):
            myRequest[key] = self._checkValidData(key, data, str)

        # optional keys
        for key in ("justification", "additionalInfo"):
            myRequest[key] = self._checkValidData(key, data, str, True)

        # theirItems is a list of dicts (each dict is one item)
        theirItems = self._checkValidData("items", data, list)

        # myItems is the list we are creating and adding to the database
        myItems = []

        # iterate through list of items
        for theirDict in theirItems:
            # theirDict = self._checkValidData(item, data, dict)
            myDict = dict()
            # iterate through keys of item dict
            for key in ("description", "partNo", "quantity", "unitCost"):
                myDict[key] = self._checkValidData(key, theirDict, str)
            myDict[key] = self._checkValidNumber("totalCost", theirDict)
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

        {
            vendor: (string, optional),
            groupID: (string, optional),
            URL: (string, optional)
        }

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
                
        if 'groupID' in data:
            myGroupID = data['groupID']
            filters.append(myGroupID)
            
        if 'URL' in data:
            myURL = data['URL']
            filters.append(myURL)

        if filters:
            bigFilter = {'$and': filters}
        else:
            bigFilter = {}

        listRequests = []
        for request in self.colRequests.find(bigFilter):
            request['_id'] = str(request['_id'])
            listRequests.append(request)

        return listRequests

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementCancel(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that the request is cancelled by the students
        and therefore unable to be edited or considered by any user.

        Expected input::

            {
                "_id": (string)
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._checkValidID(data)
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

        self._updateDocument(myID, findQuery, updateQuery, updateRule)
        
        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("manager", "admin")
    def procurementApprove(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a status submitted to the technical manager
        is approved and sent to an administrator for review.

        Expected input::

            {
                "_id": (string)
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._checkValidID(data)
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

        self._updateDocument(myID, findQuery, updateQuery, updateRule)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("manager")
    def procurementReview(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that the students who originally submitted it may
        make changes to it or cancel it.

        Expected input::

            {
                "_id": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._checkValidID(data)
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

        self._updateDocument(myID, findQuery, updateQuery, updateRule)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementResubmit(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request that had previously been sent back
        to the students for updates is now submitted back to the technical
        manager.

        Expected input::

            {
                "_id": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._checkValidID(data)
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

        self._updateDocument(myID, findQuery, updateQuery, updateRule)

        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("manager", "admin")
    def procurementReject(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request is permanently rejected and unable
        to be further edited or considered by any user.

        Expected input::

            {
                "_id": (string)
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._checkValidID(data)
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

        self._updateDocument(myID, findQuery, updateQuery, updateRule)

        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userAdd(self):
        """
        This REST endpoint takes in data for a new user and uses it to create
        a new user in the database.

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

        myRole = self._checkValidData("role", data, str)
        if myRole in ("student", "manager", "admin"):
            myUser['role'] = myRole
        else:
            cherrypy.log('Expected role of value "student", "manager", or "admin". See: %s' % myRole)
            raise cherrypy.HTTPError(400, 'Invalid role. Should be "student", "manager", or "admin".')

        for key in ("firstName", "lastName", "groupID", "netID", "email", "course"):
            myUser[key] = self._checkValidData(key, data, str)


        # TODO: make sure the user's email is unique
        # insert the data into the database
        self.colUsers.insert(myUser)

        # create a link (invitation) so the user can set a password
        myInvitation = {
            'uuid': str(uuid4()),
            'expiration': None,
            'email': myUser['email']
        }

        self.colInvitations.insert(myInvitation)
        cherrypy.log('Created new user. Setup UUID: %s' % myInvitation['uuid'])

        self.email_queue.put(('invite', {
            'email': myInvitation['email'],
            'uuid':  myInvitation['uuid'],
            'expiration': myInvitation['expiration']
        }))

        return {'uuid': myInvitation['uuid']}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userEdit(self):
        """
        This REST endpoint takes a MongoDB ObjectID and optional data fields
        for a user. The ObjectID is used to identify the user whose information
        will be edited and the optional data is what the data will be changed to.

        Expected input::

            {
                "_id": (string)
                “groupID”: (list of ints, optional),
                "firstName": (string, optional),
                "lastName": (string, optional),
                "netID": (string, optional),
                "course": (string, optional)
            }

        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myData = dict()

        myID = self._checkValidID(data)
        myData["_id"] = myID

        # groupID is optional, may be int or list of ints, is converted to list if not a list
        myGroupID = self.checkValidData("groupID", data, (int, list), True)
        if isinstance(myData["groupID"], int):
            # make list
            newList = []
            newList.append(myGroupID)
            myData["groupID"] = newList
        elif isinstance(myData["groupID"], list):
            # make sure list has only ints
            for groupID in myGroupID:
                if not isinstance(groupID, int):
                    raise cherrypy.HTTPError(400, 'groupID field must be int or list of only ints')
            myData["groupID"] = myGroupID

        # optional keys, string
        for key in ("firstName", "lastName", "netID", "course"):
            myData[key] = self._checkValidData(key, data, str, True)

        findQuery = {'_id': ObjectId(myID)}
        updateQuery = {'_id': ObjectId(myID)}


        if self.colUsers.find(findQuery).count() > 0:
            for key in ("groupID", "firstName", "lastName", "netID", "course"):
                # create update query
                updateRule = {
                    '$set':
                        {key: myData[key]}
                }
                # check that data is not default string
                if not myData[key] == "":
                    # update key
                    self._updateDocument(myID, findQuery, updateQuery, updateRule)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userRemove(self):
        """
        This REST endpoint changes the status of a user with the effect that
        the user is "removed" from the system, meaning they are no longer
        active and therefore no longer able to interact with the system.

        Expected input::

            {
                "_id": (string)
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = self._checkValidID(data)
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

        self._updateDocument(myID, findQuery, updateQuery, updateRule)

        # TODO send email?

    # don't need to check role for this
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def userVerify(self):
        """
        This REST endpoint checks that a provided email is matched with a given
        UUID, and if so, creates and stores a password hash and salt.

        Expected input::

            {
                "uuid": (string),
                "email": (string),
                "password": (string)
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myData = dict()

        # raises error if uuid, email, or password not in data
        for key in ("uuid", "email", "password"):
            myData[key] = self._checkValidData(key, data, str)

        # find invitation with given uuid
        invitation = self.colInvitations.find_one({'uuid': myData['uuid']})

        cherrypy.log("Email: %s. Invitation: %s" % (data['email'], invitation))

        # invitation may not be None, email may be None
        if invitation and invitation.get('email', None) == myData['email']:
            salt = Root.generateSalt()
            hash = Root.hashPassword(myData['password'], salt)
            self.colUsers.update({
                'email': myData['email']
            }, {'$set': {
                'salt': salt,
                'password': hash
            }})
        else:
            raise cherrypy.HTTPError(403, 'Invalid email for this invitation')

    # don't need to check role for this
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def userLogin(self):
        """
        This REST endpoint takes an email and password, checks if the hash
        is associated with the given email, and if so, logs in a user.

        Expected input::

            {
                "email": (string),
                "password": (string)
            }
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myData = dict()

        # need email and password in data
        for key in ("email", "password"):
            myData[key] = self._checkValidData(key, data, str)

        # verify password of user
        user = self.colUsers.find_one({'email': myData['email']})
        if user and self.verifyPassword(user, myData['password']):
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
        """
        Logs out a user by expiring their session.
        """
        cherrypy.lib.sessions.expire()

    # Helper functions below. DO NOT EXPOSE THESE

    def verifyPassword(self, user, password):
        """
        This function hashes a password and checks if it matches the hash of
        a given user.

        :param user: a user document from database
        :param password: a hashed password
        """
        # logging password may be security hole; do not include this line in finished product
        # cherrypy.log("verifyPassword %s ::: %s" % (user['password'], Root.hashPassword(password, user['salt'])))

        # user['password'] is hashed password, not plaintext
        # code assumes salt and password are type checked?
        if user and 'salt' in user and 'password' in user:
            return user['password'] == Root.hashPassword(password, user['salt'])
        else:
            return False

    @staticmethod
    def hashPassword(password, salt):
        """
        This function hashes a password with a given salt.

        :param password: a plaintext password
        :param salt: a random salt
        :return: the hashed password
        """
        # use pbkdf2 password hash algorithm, with sha-256 and 100,000 iterations
        # by default, encode encodes string to utf-8
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

    @staticmethod
    def generateSalt():
        """
        This function generates a random salt.

        :return: random salt
        """
        # create 32 byte salt (note: changed from 8)
        # string of random bytes
        # platform-specific (windows uses CryptGenRandom())
        return os.urandom(32)

    # checks if key value exists and is the right type
    def _checkValidData(self, key, data, dataType, optional=False, default=""):
        """
        This function takes a data dict, determines whether a key value exists
        and is the right data type. Returns the data if it is, raises an
        HTTP error if it isn't.

        :param key: the key of the data dict
        :param data: a dict of data
        :param dataType: a data type
        :param optional: True if the data did not need to be provided
        :param default: default string is ""
        :return: data, if conditions are met
        """
        if key in data:
            localVar = data[key]
            if isinstance(localVar, dataType):
                return localVar
            else:
                cherrypy.log("Expected %s of type %s. See: %s" % (key, dataType, localVar))
                raise cherrypy.HTTPError(400, 'Invalid %s format' % key)
        else:
            if not optional:
                raise cherrypy.HTTPError(400, 'Missing %s' % key)
            else:
                return default

    # checks if key value exists and is the right type (Number)
    def _checkValidNumber(self, key, data, optional=False, default=""):
        """
        This function takes a data dict, determines whether a key value exists
        and is a number. Returns the data if it is, raises an
        HTTP error if it isn't.

        :param key:
        :param data:
        :param optional:
        :param default:
        :return:
        """
        if key in data:
            localVar = data[key]
            if isinstance(localVar, (float, int)):
                return float(localVar)
            else:
                cherrypy.log("Expected %s to be a number. See: %s" % (key, localVar))
                raise cherrypy.HTTPError(400, 'Invalid %s format' % key)
        else:
            if not optional:
                raise cherrypy.HTTPError(400, 'Missing %s' % key)
            else:
                return default

    # checks if data has valid object ID
    def _checkValidID(self, data):
        """
        This function takes a data dict, determines whether it has a MongoDB
        ObjectId and that the ID is valid.

        :param data: data dict
        :return: data, if conditions are met
        """
        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                return myID
            else:
                raise cherrypy.HTTPError(400, 'Object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

    # finds document in database and updates it using provided queries
    def _updateDocument(self, myID, findQuery, updateQuery, updateRule):
        """
        This function updates a document. It finds the document in the
        database and updates it using the provided queries/rules.

        :param myID: ID of document to be updated
        :param findQuery: query to find document
        :param updateQuery: query to find document to update
        :param updateRule: rule to update document to update
        """
        if self.colRequests.find(findQuery).count() > 0:
            self.colRequests.update_one(updateQuery, updateRule, upsert=False)
        else:
            raise cherrypy.HTTPError(400, 'Request matching id and status not found in database')