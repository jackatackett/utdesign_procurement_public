#!/usr/bin/env python

import cherrypy
import os
import pymongo as pm
from bson.objectid import ObjectId
from functools import reduce

from mako.lookup import TemplateLookup

class Root(object):

    def __init__(self):
        templateDir = os.path.join(cherrypy.Application.wwwDir, 'templates')
        cherrypy.log("Template Dir: %s" % templateDir)
        self.templateLookup = TemplateLookup(directories=templateDir)
        
        client = pm.MongoClient()
        db = client['procurement']
        self.colRequests = db['requests']
        self.colUsers = db['users']

    @cherrypy.expose
    def index(self):
        template = self.templateLookup.get_template('StudentApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret
        
    @cherrypy.expose
    def debug(self):
        template = self.templateLookup.get_template('DebugApp.html')
        ret = template.render()
        cherrypy.log(str(type(ret)))
        return ret

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
        
        # array of json objects {'key': 'value"}
        
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
                if self.colRequests.find({ '$and': [ {'_id': { "$in": myID}}, {'status': 'pending'} ]  }).count() > 0:
                    self.colRequests.update({'_id': { "$set": {'status': 'cancelled'} } })
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
                if self.colRequests.find({ '$and': [ {'_id': { "$in": myID}}, {'status': 'pending'} ]  }).count() > 0:
                    self.colRequests.update({'_id': { "$set": {'status': 'approved'} } })
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
                    self.colRequests.update({'_id': ObjectId(myID)}, {"$set": {'status': 'rejected'} })
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
        """
        #check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')
            
        myUser = dict()
        
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
       
            
        # insert the data into the database
        self.colUsers.insert(myUser)

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
                    self.colUsers.update({'_id': ObjectId(myID)}, {"$set": data })
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
