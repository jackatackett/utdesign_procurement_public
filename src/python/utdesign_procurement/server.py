#!/usr/bin/env python

import cherrypy
import hashlib
import os
import pymongo as pm

from bson.objectid import ObjectId
from functools import reduce
from mako.lookup import TemplateLookup
from uuid import uuid4, UUID

class Root(object):

    def __init__(self):
        templateDir = os.path.join(cherrypy.Application.wwwDir, 'templates')
        cherrypy.log("Template Dir: %s" % templateDir)
        self.templateLookup = TemplateLookup(directories=templateDir)

        client = pm.MongoClient()
        db = client['procurement']
        self.colRequests = db['requests']
        self.colUsers = db['users']
        self.colInvitations = db['invitations']

    # Pages go below

    @cherrypy.expose
    def index(self):
        """
        This is the login view.

        TODO: If they're already logged in, then they get redirected to their proper view.
        """
        template = self.templateLookup.get_template('login/LoginApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

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
    def student(self):
        template = self.templateLookup.get_template('student/StudentApp.html')
        ret = template.render()
        return ret

    @cherrypy.expose
    def manager(self):
        template = self.templateLookup.get_template('manager/ManagerApp.html')
        ret = template.render()
        return ret

    @cherrypy.expose
    def admin(self):
        template = self.templateLookup.get_template('admin/ AdminApp.html')
        ret = template.render()
        return ret

    @cherrypy.expose
    def debug(self):
        template = self.templateLookup.get_template('debug/DebugApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

    # API Functions go below

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def procurementRequest(self):
        """
        Would like to rework the code to promote re-use and such.
        Also check to make sure it all/any of it works.
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')
        
        myRequest = dict()
        
        # set default value of value in dict
        myRequest['status'] = 'pending'
        
        # check for value in data, check value is of correct type, add value to dict
        if 'vendor' in data:
            myVendor = data['vendor']
            if isinstance(myVendor, str):
                myRequest['vendor'] = myVendor
            else:
                cherrypy.log("Expected vendor of type str. See: %s" % myVendor)
                raise cherrypy.HTTPError(400, 'Invalid vendor format')
        else:
            raise cherrypy.HTTPError(400, 'Missing vendor')
              
        # check for value in data, check value is of correct type, add value to dict
        if 'token' in data:
            myToken = data['token']
            if isinstance(myToken, str):
                myRequest['token'] = myToken
            else:
                cherrypy.log("Expected token of type str. See: %s" % myToken)
                raise cherrypy.HTTPError(400, 'Invalid token format')
        else:
            raise cherrypy.HTTPError(400, 'Missing token')

        # check for value in data, check value is of correct type, add value to dict                
        if 'groupID' in data:
            myGroupID = data['groupID']
            if isinstance(myGroupID, str):
                myRequest['groupID'] = myGroupID
            else:
                cherrypy.log("Expected groupID of type str. See: %s" % myGroupID)
                raise cherrypy.HTTPError(400, 'Invalid groupID format')
        else:
            raise cherrypy.HTTPError(400, 'Missing group ID')

        #TODO check that data['items'] exists
        if hasattr(data['items'], '__iter__'):
            myItem = dict()
            for item in data['items']:
                if isinstance(item, dict):
                    if 'description' in item:
                        myDescription = item['description']
                        if isinstance(myGroupID, str):
                            myRequest['groupID'] = myGroupID
                        else:
                            cherrypy.log("Expected description of type str. See: %s" % myGroupID)
                            raise cherrypy.HTTPError(400, 'Invalid description format')
                    else:
                        raise cherrypy.HTTPError(400, 'Missing description')

                    if 'partNo' in item:
                        myPartNo = item['partNo']
                        if isinstance(myPartNo, str):
                            myRequest['partNo'] = myPartNo
                        else:
                            cherrypy.log("Expected partNo of type str. See: %s" % myPartNo)
                            raise cherrypy.HTTPError(400, 'Invalid partNo format')
                    else:
                        raise cherrypy.HTTPError(400, 'Missing partNo')

                    if 'quantity' in item:
                        myQuantity = item['quantity']
                        if isinstance(myQuantity, str):
                            myRequest['quantity'] = myQuantity
                        else:
                            cherrypy.log("Expected quantity of type str. See: %s" % myQuantity)
                            raise cherrypy.HTTPError(400, 'Invalid quantity format')
                    else:
                        raise cherrypy.HTTPError(400, 'Missing quantity')

                    if 'unitCost' in item:
                        myUnitCost = item['unitCost']
                        if isinstance(myUnitCost, str):
                            myRequest['unitCost'] = myUnitCost
                        else:
                            cherrypy.log("Expected unitCost of type str. See: %s" % myUnitCost)
                            raise cherrypy.HTTPError(400, 'Invalid unitCost format')
                    else:
                        raise cherrypy.HTTPError(400, 'Missing unitCost')

                else:
                    raise cherrypy.HTTPError(400, 'Invalid item format')
        else:
            raise cherrypy.HTTPError(400, 'Invalid item format')

        # the following data fields are optional
        if 'URL' in data:
            myURL = data['URL']
            if isinstance(myURL, str):
                myRequest['URL'] = myURL
            else:
                raise cherrypy.HTTPError(400, 'Invalid URL format')

            
        if 'justification' in data:
            myJust = data['justification']
            if isinstance(myJust, str):
                myRequest['justification'] = myJust
            else:
                raise cherrypy.HTTPError(400, 'Invalid justification format')
            
            
        if 'additionalInfo' in data:
            myAdd = data['additionalInfo']
            if isinstance(myAdd, str):
                myRequest['additionalInfo'] = myAdd
            else:
                raise cherrypy.HTTPError(400, 'Invalid additional info format')
            
        # insert the data into the database
        self.colRequests.insert(myRequest)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
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

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def procurementCancel(self):
        """
        
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')
            
        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                # request exists in database matching id with status 'pending' or 'review'
                if self.colRequests.find({ '$and': [ {'_id': ObjectId(myID)}, {'$or' : [ {'status': 'pending'}, {'status': 'review'} ] } ]  }).count() > 0:
                    # update request to set status to cancelled
                    self.colRequests.update_one({'_id': ObjectId(myID)}, {'$set': {'status': 'cancelled'}}, upsert=False )
                else:
                    raise cherrypy.HTTPError(400, 'Pending request matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')
        
        

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
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
            
        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                # if there exists a request with the given id whose status is 'pending', update the request's status to 'approved'
                if self.colRequests.find({ '$and': [ {'_id': ObjectId(myID)}, {'status': 'pending'} ] } ).count() > 0:
                    self.colRequests.update_one({'_id': ObjectId(myID)}, {'$set': {'status': 'approved'}}, upsert=False )
                else:
                    raise cherrypy.HTTPError(400, 'Pending request matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def procurementReview(self):
        """
        Need to make code pretty, check it works.
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                # if there exists a request with the given id whose status is 'approved' or 'pending', update the request's status to 'review'
                if self.colRequests.find({ '$and': [ {'_id': ObjectId(myID)}, { '$or': [ {'status': 'approved'}, {'status': 'pending'} ]} ]}).count() > 0:
                    self.colRequests.update({'_id': ObjectId(myID)}, {"$set": {'status': 'review'} }, upsert=False )
                else:
                    raise cherrypy.HTTPError(400, 'Pending request matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def procurementResubmit(self):
        """
        Need to make code pretty, check it works.
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                # if there exists a request with the given id whose status is 'review', update the request's status to 'pending'
                if self.colRequests.find({'$and': [{'_id': ObjectId(myID)}, {'status': 'review'}, ] } ).count() > 0:
                    self.colRequests.update({'_id': ObjectId(myID)}, {"$set": {'status': 'pending'}}, upsert=False)
                else:
                    raise cherrypy.HTTPError(400, 'Pending request matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')



    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def procurementReject(self):
        """
        Need to make code pretty, check it works.
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')
            
        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                # if there exists a request with the given id whose status is either 'pending' or 'approved', update the request's status to 'rejected'
                if self.colRequests.find({ '$and': [ {'_id': ObjectId(myID)}, { '$or': [{'status': 'pending'}, {'status': 'approved' } ] } ] }).count() > 0:
                    self.colRequests.update({'_id': ObjectId(myID)}, {"$set": {'status': 'rejected'} }, upsert=False )
                else:
                    raise cherrypy.HTTPError(400, 'Pending request matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
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
                "course": (string)
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

        if 'groupID' in data:
            myGroupID = data['groupID']
            if isinstance(myGroupID, str):
                myUser['groupID'] = myGroupID
            else:
                cherrypy.log("Expected groupID of type str. See: %s" % myGroupID)
                raise cherrypy.HTTPError(400, 'Invalid groupID format')
        else:
            raise cherrypy.HTTPError(400, 'Missing group ID')
        
        if 'firstName' in data:
            myFirstName = data['firstName']
            if isinstance(myFirstName, str):
                myUser['firstName'] = myFirstName
            else:
                cherrypy.log("Expected firstName of type str. See: %s" % myFirstName)
                raise cherrypy.HTTPError(400, 'Invalid firstName format')
        else:
            raise cherrypy.HTTPError(400, 'Missing first name')
            
            
        if 'lastName' in data:
            myLastName = data['lastName']
            if isinstance(myLastName, str):
                myUser['lastName'] = myLastName
            else:
                cherrypy.log("Expected lastName of type str. See: %s" % myLastName)
                raise cherrypy.HTTPError(400, 'Invalid lastName format')
        else:
            raise cherrypy.HTTPError(400, 'Missing last name')
                
        if 'netID' in data:
            myNetID = data['netID']
            if isinstance(myNetID, str):
                myUser['netID'] = myNetID
            else:
                cherrypy.log("Expected netID of type str. See: %s" % myNetID)
                raise cherrypy.HTTPError(400, 'Invalid netID format')
        else:
            raise cherrypy.HTTPError(400, 'Missing net id')
            
        if 'email' in data:
            myEmail = data['email']
            if isinstance(myEmail, str):
                myUser['email'] = myEmail
            else:
                cherrypy.log("Expected email of type str. See: %s" % myEmail)
                raise cherrypy.HTTPError(400, 'Invalid email format')
        else:
            raise cherrypy.HTTPError(400, 'Missing email')
            
        if 'course' in data:
            myCourse = data['course']
            if isinstance(myCourse, str):
                myUser['course'] = myCourse
            else:
                cherrypy.log("Expected course of type str. See: %s" % myCourse)
                raise cherrypy.HTTPError(400, 'Invalid course format')
        else:
            raise cherrypy.HTTPError(400, 'Missing course')    
       

        # TODO: make sure the user's email is unique
        # insert the data into the database
        self.colUsers.insert(myUser)

        # create a link so the user can set a password

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
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
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
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def userRemove(self):
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')
            
        if '_id' in data:
            myID = data['_id']
            if ObjectId.is_valid(myID):
                # if there exists a user with the given id whose status is 'current', update the user's status to 'removed'
                if self.colUsers.find({ '$and': [ {'_id': ObjectId(myID)}, {'status': 'current'} ]  }).count() > 0:
                    self.colUsers.update_one({'_id': ObjectId(myID)}, {'$set': {'status': 'removed'}}, upsert=False )
                    
                #~ usr = self.colUsers.find_one({'_id': ObjectId(myID)})
                #~ if usr and 'status' in usr and usr['status'] == 'current':
                    #~ cow = self.colUsers.update_one({'_id': ObjectId(myID)}, {'$set': {'status': 'removed'}}, upsert=False )
                    
                else:
                    raise cherrypy.HTTPError(400, 'Current user matching id not found in database')
            else:
                raise cherrypy.HTTPError(400, 'object id not valid')
        else:
            raise cherrypy.HTTPError(400, 'data needs object id')

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
        # auth is helpful for debugging
        auth = 'role' in cherrypy.session
        ret =  {'authenticated': auth}

        if auth:
            for k in ('role', 'email'):
                ret[k] = cherrypy.session[k]

        # ret is a JSON object containing role and email, and a boolean
        # "authenticated"
        return ret

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
    cherrypy.tree.mount(Root(), '/', config=server_config)

    cherrypy.engine.start()
    input()
    cherrypy.engine.stop()

if __name__ == '__main__':
    main()
