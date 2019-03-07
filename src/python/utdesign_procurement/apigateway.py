#!/usr/bin/env python3

import cherrypy
import pymongo as pm

from bson.objectid import ObjectId
from uuid import uuid4

from utdesign_procurement.utils import authorizedRoles, generateSalt, hashPassword, \
    checkProjectNumbers, checkValidData, checkValidID, checkValidNumber, \
    verifyPassword

class ApiGateway(object):

    def __init__(self, email_queue):

        self.email_queue = email_queue

        client = pm.MongoClient()
        db = client['procurement']
        self.colRequests = db['requests']
        self.colUsers = db['users']
        self.colInvitations = db['invitations']

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
                "projectNumber": (int or list of int),
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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myRequest = dict()

        # set default value of status to pending
        myRequest['status'] = 'pending'

        # mandatory projectNumber
        myRequest['projectNumber'] = checkValidData('projectNumber', data, int)

        # mandatory keys
        for key in ("vendor", "URL"):
            myRequest[key] = checkValidData(key, data, str)

        # optional keys
        for key in ("justification", "additionalInfo"):
            myRequest[key] = checkValidData(key, data, str, True)

        # theirItems is a list of dicts (each dict is one item)
        theirItems = checkValidData("items", data, list)

        # myItems is the list we are creating and adding to the database
        myItems = []

        # iterate through list of items
        for theirDict in theirItems:
            # theirDict = checkValidData(item, data, dict)
            myDict = dict()
            # iterate through keys of item dict
            for key in ("description", "partNo", "quantity", "unitCost"):
                myDict[key] = checkValidData(key, theirDict, str)
            myDict['totalCost'] = checkValidNumber("totalCost", theirDict)
            myItems.append(myDict)

        myRequest["items"] = myItems

        # insert the data into the database
        self.colRequests.insert(myRequest)

        # TODO send email

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student", "manager", "admin")
    def procurementStatuses(self):
        """
        Returns a list of procurement requests matching all provided filters.
        Currently matches with any combination of vendor, projectNumbers, and
        URL. For non-admin users, projectNumbers will be restricted only to
        those projectNumbers which the user is authorized to view. Ignores
        projectNumbers that the user is not authorized to view.

        {
            vendor: (string, optional),
            projectNumbers: (int or list of ints, optional),
            URL: (string, optional)
        }

        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = None


        filters = []

        if 'vendor' in data:
            myVendor = checkValidData('vendor', data, str)
            filters.append({'vendor': {'$eq': myVendor}})

        if 'projectNumbers' in data:
            myProjects = checkProjectNumbers(data)
            if cherrypy.session['role'] == 'admin':
                filters.append({'projectNumber': {'$in': myProjects}})

            # non-admins are limited to their projectNumbers
            else:
                validPNos = []
                for pNo in cherrypy.session['projectNumbers']:
                    if pNo in myProjects:
                        validPNos.append(pNo)

                if validPNos:
                    filters.append({'projectNumber': {'$in': validPNos}})

        # non-admins are limited to their projectNumbers
        elif cherrypy.session['role'] != 'admin':
            filters.append({
                'projectNumber': {
                    '$in': cherrypy.session['projectNumbers']
                }
            })

        if 'URL' in data:
            myURL = checkValidData('URL', data, str)
            filters.append({'URL': {'$eq': myURL}})

        if filters:
            bigFilter = {'$and': filters}
        else:
            bigFilter = {}

        listRequests = []
        for request in self.colRequests.find(bigFilter):
            request['_id'] = str(request['_id'])
            del request['timestamp'] #TODO marshal the timestamp properly
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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
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

        myID = checkValidID(data)
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

        myID = checkValidID(data)
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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
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
                "projectNumbers": (int or list of ints),
                "firstName": (string),
                "lastName": (string),
                "netID": (string),
                "email": (string),
                "course": (string),
                "role": (string)
            }

        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myUser = dict()

        # set default value of value in dict
        myUser['status'] = 'current'

        myRole = checkValidData("role", data, str)
        if myRole in ("student", "manager", "admin"):
            myUser['role'] = myRole
        else:
            cherrypy.log(
                'Expected role of value "student", "manager", or "admin". '
                'See: %s' % myRole)
            raise cherrypy.HTTPError(
                400, 'Invalid role. Should be "student", "manager", or '
                     '"admin".')

        myUser['projectNumbers'] = checkProjectNumbers(data)

        for key in ("firstName", "lastName", "netID", "email", "course"):
            myUser[key] = checkValidData(key, data, str)


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
        will be edited and the optional data is what the data will be changed
        to.

        Expected input::

            {
                "_id": (string)
                “projectNumbers”: (list of ints, optional),
                "firstName": (string, optional),
                "lastName": (string, optional),
                "netID": (string, optional),
                "course": (string, optional)
            }

        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # the newly changed fields
        myData = dict()

        # the MongoDB _id of the record to change
        myID = checkValidID(data)

        # the optional projectNumbers of the user
        if 'projectNumbers' in data:
            myData = checkProjectNumbers(data)

        # optional keys, string
        for key in ("firstName", "lastName", "netID", "course"):
            if key in data:
                myData[key] = checkValidData(key, data, str)

        # update the document
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {'$set': myData}
        self._updateDocument(myID, updateQuery, updateQuery, updateRule)

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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myData = dict()

        # raises error if uuid, email, or password not in data
        for key in ("uuid", "email", "password"):
            myData[key] = checkValidData(key, data, str)

        # find invitation with given uuid
        invitation = self.colInvitations.find_one({'uuid': myData['uuid']})

        cherrypy.log("Email: %s. Invitation: %s" % (data['email'], invitation))

        # invitation may not be None, email may be None
        if invitation and invitation.get('email', None) == myData['email']:
            salt = generateSalt()
            hash = hashPassword(myData['password'], salt)
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
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myData = dict()

        # need email and password in data
        for key in ("email", "password"):
            myData[key] = checkValidData(key, data, str)

        # verify password of user
        user = self.colUsers.find_one({'email': myData['email']})
        if user and verifyPassword(user, myData['password']):
            cherrypy.session['email'] = user['email']
            cherrypy.session['role'] = user['role']
            cherrypy.session['projectNumbers'] = user.get('projectNumbers', [])
            return "<strong> You logged in! </strong>"
        else:
            raise cherrypy.HTTPError(403, 'Invalid email or password.')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @authorizedRoles("student", "manager")
    def userProjects(self):
        """
        This REST endpoint returns a list of projectNumbers associated with
        the authenticated user.

        Returns ::

            {
                'projectNumbers': (list of ints)
            }

        """
        return cherrypy.session.get('projectNumbers', [])

    # this function is for debugging for now. If that never changes then
    # TODO remove this function before production if it isn't needed
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def userInfo(self):
        # auth/authenticated is helpful for debugging
        auth = 'role' in cherrypy.session
        ret =  {'authenticated': auth}

        if auth:
            for k in ('role', 'email', 'projectNumbers'):
                ret[k] = cherrypy.session[k]

        # ret is a JSON object containing role and email, and a boolean
        # "authenticated"
        return ret

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userPages(self):
        """
            returns an int
        """

        pageSize = 10 # TODO make this configurable
        d, m = divmod(self.colUsers.find().count(), pageSize)
        return d+1 if m else d

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userData(self):
        """

        Incoming ::
        {
            'sortBy': (string in projectNumbers, firstName, lastName, netID,
                email, course, role, status)
                (Optional. Default "email")
            'order': (string in 'ascending', 'descending')
                (Optional. Default: "ascending")
            'pageNumber': (int)
                (Optional. Default: 0)
        }

        Outgoing ::
        [
            {
                “projectNumbers”: (list of ints),
                "firstName": (string),
                "lastName": (string),
                "netID": (string),
                "email": (string),
                "course": (string),
                “role”: “student”,
                “status”: (string), //”current” or “removed”
            }
        ]

        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        sortBy = checkValidData('sortBy', data, str, default='email',
                                optional=True)

        if sortBy not in ('projectNumbers', 'firstName', 'lastName', 'netID',
                'email', 'course', 'role', 'status'):
            raise cherrypy.HTTPError(
                400, 'sortBy must be any of projectNumbers, firstName, '
                     'lastName, netID, email, course, role, status. Not %s'
                     % sortBy)

        order = checkValidData('order', data, str, default='ascending',
                                optional=True)

        if order not in ('ascending', 'descending'):
            raise cherrypy.HTTPError(
                400, 'order must be ascending or descending. Not %s.' % order)

        direction = pm.ASCENDING if order == 'ascending' else pm.DESCENDING

        pageNumber = checkValidData('pageNumber', data, int, default=0,
                                optional=True)

        pageSize = 10 # TODO stretch goal make this configurable

        userCursor = self.colUsers.find().sort(sortBy, direction)

        retUsers = []
        for user in userCursor[pageSize*pageNumber: pageSize*(pageNumber+1)]:
            myUser = dict()
            myUser['_id'] = str(user['_id'])
            for key in ('firstName', 'lastName', 'email', 'status', 'role'):
                myUser[key] = user[key]

            myUser['netID'] = user.get('netID', '')

            if myUser['role'] != 'admin':
                for key in ('projectNumbers', 'course'):
                    myUser[key] = user[key]

            retUsers.append(myUser)

        return retUsers

    @cherrypy.expose
    def userLogout(self):
        """
        Logs out a user by expiring their session.
        """
        cherrypy.lib.sessions.expire()

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
            raise cherrypy.HTTPError(
                400, 'Request matching id and status not found in database')
