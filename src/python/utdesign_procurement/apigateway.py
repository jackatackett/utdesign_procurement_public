#!/usr/bin/env python3

import cherrypy
import os
import pymongo as pm
import pandas as pd
import xlsxwriter

from bson.objectid import ObjectId
from io import BytesIO
from uuid import uuid4

from utdesign_procurement.utils import (authorizedRoles, generateSalt,
    hashPassword, checkProjectNumbers, checkValidData, checkValidID,
    checkValidNumber, verifyPassword, requestCreate, convertToCents,
    getKeywords, getProjectKeywords, getRequestKeywords, lenientConvertToCents)

from datetime import datetime, timedelta

absDir = os.getcwd()

class ApiGateway(object):

    def __init__(self, email_handler):

        self.email_handler = email_handler

        client = pm.MongoClient()
        db = client['procurement']
        self.colRequests = db['requests']
        self.colUsers = db['users']
        self.colInvitations = db['invitations']
        self.colCosts = db['costs']
        self.colProjects = db['projects']

        self.colSequence = db['sequence']
        self.reportUUIDs = []

    # API Functions go below. DO EXPOSE THESE

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("student", "admin")
    def procurementSave(self):
        """
        This REST endpoint takes data as an input as uses the data to create
        a procurement request and save it to the database. If the submit flag
        is true, the request will be submitted to the TM, and if not, it won't.

        Expected input::

            {
                "submit": (Boolean) optional (not optional if submitted by student),
                "adminEdit": (Boolean) optional (not optional if admin performs an edit),
                "status": (string) optional (not optional if admin performs an edit),
                "requestNumber": (int) optional,
                "manager": (string), //email of manager who can approve this
                "vendor": (string),
                "projectNumber": (int),
                "URL": (string),
                "justification": (string) optional,
                "additionalInfo": (string) optional,
                "items": [
                    {
                    "description": (string),
                    "partNo": (string),
                    "itemURL": (string),
                    "quantity": (integer),
                    "unitCost": (string),
                    "totalCost": (string)
                    }
                ]
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # check if projectNumber belongs to active project; if not, don't allow request to be saved
        myProjectNumber = checkValidData("projectNumber", data, int)
        findQuery = {
            "projectNumber": myProjectNumber,
            "status": 'active'
        }
        if not self.colProjects.find_one(findQuery):
            raise cherrypy.HTTPError(400, "projectNumber inactive")  # TODO better message

        # check if admin is editing, or student submitting/saving
        mySubmit = None
        myAdminEdit = None

        if "adminEdit" in data:
            if "status" not in data:
                raise cherrypy.HTTPError(400, "Bad data given")
            myAdminEdit = checkValidData("adminEdit", data, bool)
            if not myAdminEdit:
                raise cherrypy.HTTPError(400, "Bad data given")
            myStatus = checkValidData("status", data, str)
        elif "submit" in data:
            mySubmit = checkValidData("submit", data, bool)

        if myAdminEdit is None and mySubmit is None:
            raise cherrypy.HTTPError(400, "Bad submission info provided")

        # if a student is saving, fields are optional, otherwise all are required
        # admin edit doesn't change status. Submit goes to "pending", save goes to "saved"
        if myAdminEdit:
            status = myStatus
            optional = False
        elif mySubmit:
            status = "pending"
            optional = False
        else:
            status = "saved"
            optional = True

        # get the request number if any. Generate one if not.
        if "requestNumber" in data:
            myRequestNumber = data["requestNumber"]
        else:
            myRequestNumber = self.sequence()

        # sanitize the input
        myRequest = requestCreate(data, status, optional)
        myRequest['requestNumber'] = myRequestNumber
        myRequest['oic'] = 0

        query = {"requestNumber": myRequestNumber}

        # if pending, append new history to this
        oldRequest = self.colRequests.find_one(query)

        # find old history
        if oldRequest is not None and 'history' in oldRequest:
            oldHistory = oldRequest['history']
        else:
            oldHistory = [] #initialize history

        # find old state if oldHistory has an old state
        if len(oldHistory) and 'newState' in oldHistory[-1]:
            oldState = oldHistory[-1]['newState']
        else:
            oldState = 'saved' # old state is "saved" if there isn't an old state in the database?

        if myAdminEdit:
            oldHistory.append({
                "actor": cherrypy.session["email"],
                "timestamp": datetime.now(),
                "comment": "edited by " + cherrypy.session["email"],
                "oldState": oldState,
                "newState": oldState
            })
        elif status == "pending":
            oldHistory.append({
                "actor": cherrypy.session["email"],
                "timestamp": datetime.now(),
                "comment": "submitted by " + cherrypy.session["email"],
                "oldState": oldState,
                "newState": "pending"
            })

        myRequest["history"] = oldHistory

        # insert the data into the database
        self.colRequests.replace_one(query, myRequest, upsert=True)

        # send emails only if status is pending i.e. request is officially submitted
        if status == 'pending':
            #send confirmation emails to students and notification to manager
            teamEmails = self.getTeamEmails(myRequest['projectNumber'])
            self.email_handler.procurementSave(**{
                'teamEmails': teamEmails,
                'request': myRequest,
            })

        elif myAdminEdit:
            #notify students and manager that admin has updated the request
            teamEmails = self.getTeamEmails(myRequest["projectNumber"])
            self.email_handler.procurementEditAdmin(**{
                'teamEmails': teamEmails,
                'request': myRequest,
            })

    def sequence(self):
        """
        Checks the current sequence value of requests, returns it,
        and increments the value.
        :return:
        """

        query = {"name": "requests"}
        current = self.colSequence.find_one(query)

        if not current or 'number' not in current:
            raise cherrypy.HTTPError(500, "Fatal error! No sequence found for requests.")

        current = current['number']

        updateRule = {"$set":
                          {"number": current + 1}
                    }

        self.colSequence.update_one(query, updateRule)

        return int(current)


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("student")
    def managerList(self):
        """
        Takes a projectNumber and returns a list of technical managers who
        are assigned to that project

        Expected input::

            {
                "projectNumber": (int)
            }
        :return:
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myProjectNumber = checkValidNumber("projectNumber", data)

        if myProjectNumber not in cherrypy.session['projectNumbers']:
            raise cherrypy.HTTPError(403, "invalid projectNumber")

        query = {
            "$and": [
                {"role": "manager"},
                {"projectNumbers": myProjectNumber}
            ]
        }

        managers = []

        for man in self.colUsers.find(query):
            managers.append(man['email'])

        return managers

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
            URL: (string, optional),
            statuses: (string or list of strings, optional)
        }

        If the user is a manager, they will not be able to see "saved" requests
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = dict()


        filters = []

        if 'vendor' in data:
            myVendor = checkValidData('vendor', data, str)
            filters.append({'vendor': {'$eq': myVendor}})

        if 'statuses' in data:
            myStatuses = checkValidData('statuses', data, list)
            for s in myStatuses:
                if not isinstance(s, str):
                    raise cherrypy.HTTPError(400, "Invalid status type: %s" % s)
            filters.append({'status': {'$in': myStatuses}})

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

        # managers should not see saved things
        if cherrypy.session['role'] == 'manager':
            filters.append({'status': {'$ne': 'saved'}})
            filters.append({'status': {'$ne': 'cancelled'}})

        # if list isn't empty
        if filters:
            bigFilter = {'$and': filters}
        else:
            bigFilter = {}

        listRequests = []
        for request in self.colRequests.find(bigFilter):
            request['_id'] = str(request['_id'])
            if 'history' in request:
                for hist in range(len(request['history'])):
                    if 'timestamp' in request['history'][hist]:
                        request['history'][hist]['timestamp'] = request['history'][hist]['timestamp'].isoformat(' ')[0:16]
            listRequests.append(request)

        return listRequests

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementEditAdmin(self):
        """
        This REST endpoint allows an admin to edit a procurement request.

        Expected input::
            {
                "vendor": (string) optional,
                "URL": (string) optional,
                "items": [
                    {
                    "description": (string) optional,
                    "partNo": (string) optional,
                    "itemURL": (string) optional,
                    "quantity": (integer) optional,
                    "unitCost": (string)optional ,
                    "totalCost": (string) optional
                    }
                ]
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = dict()

        requestChanges = dict()

        for key in ("vendor", "URL"):
            if data[key]:
                requestChanges[key] = checkValidData(key, data, str)



        # TODO validate inputs
        # TODO add history
        # TODO send confirmation email to admin
        # TODO send notification emails to students

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

        # TODO check this action is allowed

        myID = checkValidID(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {
                    '$or': [
                        {'status': "updates for manager"},
                        {'status': "updates for admin"},
                        {'status': "saved"}
                    ]
                }
            ]
        }
        updateQuery = {'_id': ObjectId(myID)}
        currentState = list(self.colRequests.find(findQuery))[0]["status"]
        updateRule = {'$set':
                          {'status': "cancelled"},
                      "$push":
                          {"history":
                            {
                            "actor": cherrypy.session["email"],
                            "timestamp": datetime.now(),
                            "comment": "cancelled by user",
                            "oldState": currentState,
                            "newState": "cancelled"
                            }
                          }
                      }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        # send confirmation emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.confirmStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'cancelled'
        })

        # if need to send email to manager
        if myRequest['oic'] >= 1:
            self.email_handler.notifyCancelled(**{
                'email': myRequest['manager'],
                'requestNumber': myRequest['requestNumber'],
                'projectNumber': myRequest['projectNumber'],
            })

        # if need to send email to admin
        if myRequest['oic'] == 2:
            adminEmails = self.getAdminEmails()
            self.email_handler.notifyCancelled(**{
                'email': adminEmails,
                'requestNumber': myRequest['requestNumber'],
                'projectNumber': myRequest['projectNumber'],
            })

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("manager")
    def procurementApproveManager(self):
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

        # TODO check this action is allowed

        myID = checkValidID(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "pending"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            '$set':
                {'status': "manager approved"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": "approved by manager",
                    "oldState": "pending",
                    "newState": "manager approved"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        if myRequest['oic'] == 0:
            myRequest['oic'] = 1

        # send confirmation email to manager
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'approved'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'approved by manager',
            'user': cherrypy.session['email'],
            'role': 'manager'
        })

        # send notification emails to admins
        adminEmails = self.getAdminEmails()
        self.email_handler.notifyRequestAdmin(**{
            'adminEmails': adminEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber']
        })

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("manager")
    def procurementUpdateManager(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that the students who originally submitted it may
        make changes to it or cancel it.

        Expected input::

            {
                "_id": (string),
                "comment": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
        myComment = checkValidData("comment", data, str)
        if myComment == "":
            myComment = "No comment"
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "pending"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "updates for manager"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": myComment,
                    "oldState": "pending",
                    "newState": "updates for manager"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        if myRequest['oic'] == 0:
            myRequest['oic'] = 1

        # send confirmation email to manager
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'sent back to the students for updates'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudentRejected(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'sent back to you for updates',
            'user': cherrypy.session['email'],
            'role': 'manager',
            'comment': myComment
        })


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementUpdateManagerAdmin(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that the students who originally submitted it may
        make changes to it or cancel it.

        Expected input::

            {
                "_id": (string),
                "comment": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)

        myComment = checkValidData("comment", data, str)
        if myComment == "":
            myComment = "No comment"

        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "manager approved"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "updates for manager"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": myComment,
                    "oldState": "manager approved",
                    "newState": "updates for manager"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        if myRequest['oic'] == 1:
            myRequest['oic'] = 2

        # send confirmation email to admin
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'sent back to the students for updates'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudentRejected(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'sent back to you for updates',
            'user': cherrypy.session['email'],
            'role': 'admin',
            'comment': myComment
        })

        # send notification email to manager
        managerEmail = myRequest['manager']
        self.email_handler.notifyUpdateManager(**{
            'email': managerEmail,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber']
        })


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementResubmitToManager(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request that had previously been sent back
        to the students for updates is now submitted back to the technical
        manager.

        Expected input::

            {
                "_id": (string),

                "requestNumber": (int) optional,
                "manager": (string), //email of manager who can approve this
                "vendor": (string),
                "projectNumber": (int),
                "URL": (string),
                "justification": (string) optional,
                "additionalInfo": (string) optional,
                "items": [
                    {
                    "description": (string),
                    "partNo": (string),
                    "itemURL": (string),
                    "quantity": (integer),
                    "unitCost": (string),
                    "totalCost": (string)
                    }
                ]
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # TODO check this action is allowed

        myRequest = requestCreate(data, status='pending', optional=False)

        myID = checkValidID(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "updates for manager"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}

        # find old history and append to myRequest
        oldHistory = self.colRequests.find_one(findQuery)["history"]   #will have history
        oldHistory.append({
            "actor": cherrypy.session["email"],
            "timestamp": datetime.now(),
            "comment": "submitted by " + cherrypy.session["email"],
            "oldState": "updates for manager",
            "newState": "pending"
        })
        myRequest["history"] = oldHistory

        updateRule = {"$set": myRequest}

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementResubmitToManger: missing request with id %s" % myID)
            return

        # send confirmation emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.confirmStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'resubmitted to manager'
        })

        # send notification email to manager
        self.email_handler.notifyRequestManager(**{
            'email': myRequest['manager'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber']
        })

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("student")
    def procurementResubmitToAdmin(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request that had previously been sent back
        to the students for changes is now submitted back to the admin.

        Expected input::

             {
                "_id": (string),

                "requestNumber": (int) optional,
                "manager": (string), //email of manager who can approve this
                "vendor": (string),
                "projectNumber": (int),
                "URL": (string),
                "justification": (string) optional,
                "additionalInfo": (string) optional,
                "items": [
                    {
                    "description": (string),
                    "partNo": (string),
                    "itemURL": (string),
                    "quantity": (integer),
                    "unitCost": (string),
                    "totalCost": (string)
                    }
                ]
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # TODO check this action is allowed

        myRequest = requestCreate(data, 'manager approved', False)

        myID = checkValidID(data)
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "updates for admin"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}

        # find old history and append to myRequest
        oldHistory = self.colRequests.find_one(findQuery)["history"]   #will have history
        oldHistory.append({
            "actor": cherrypy.session["email"],
            "timestamp": datetime.now(),
            "comment": "submitted by " + cherrypy.session["email"],
            "oldState": "updates for admin",
            "newState": "manager approved"
        })
        myRequest["history"] = oldHistory

        updateRule = {"$set": myRequest}

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementResubmitToAction: missing request with id %s" % myID)
            return

        # send confirmation emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.confirmStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'resubmitted to admin'
        })

        # send notification emails to admins
        adminEmails = self.getAdminEmails()
        self.email_handler.notifyRequestAdmin(**{
            'adminEmails': adminEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber']
        })

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementUpdateAdmin(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request is sent back to the students who
        originally submitted it in order to make small changes.

        Expected input::

            {
                "_id": (string),
                "comment": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
        myComment = checkValidData("comment", data, str)
        if myComment == "":
            myComment = "No comment"

        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "manager approved"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "updates for admin"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": myComment,
                    "oldState": "manager approved",
                    "newState": "updates for admin"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)


        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        if myRequest['oic'] == 1:
            myRequest['oic'] = 2

        # send confirmation email to admin
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'sent back to the students for updates'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudentRejected(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'sent back to you for updates',
            'user': cherrypy.session['email'],
            'role': 'admin',
            'comment': myComment
        })

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementOrder(self):
        """
        This REST endpoint changes the status of a procurement request
        to reflect that its items have been ordered by an admin.
        The shipping cost is also set.

        Expected input::

            {
                "_id": (string),
                "amount": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
        shippingAmt = lenientConvertToCents(checkValidData("amount", data, str))
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "manager approved"}
            ]}
        try:
            doc = list(self.colRequests.find(findQuery))[0]
            totalAmt = int(doc["requestTotal"]) + shippingAmt
            #~ print()
            #~ print(totalAmt)
            #~ print()
            #~ totalAmt = totalAmt[0]["requestTotal"]
            updateQuery = {'_id': ObjectId(myID)}
            updateRule = {
                "$set":
                    {'status': "ordered",
                     'shippingCost': shippingAmt,
                     'requestTotal': totalAmt},
                "$push":
                    {"history":
                        {
                        "actor": cherrypy.session["email"],
                        "timestamp": datetime.now(),
                        "comment": "marked as ordered by admin",
                        "oldState": "manager approved",
                        "newState": "ordered"
                        }
                    }
            }

            self._updateDocument(findQuery, updateQuery, updateRule)

            self.calculateBudget(doc["projectNumber"])

        except:
            raise cherrypy.HTTPError(400, "Error updating shipping")
        
        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        # send confirmation email to admin
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'marked as ordered'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'ordered',
            'user': cherrypy.session['email'],
            'role': 'admin'
        })
       
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementReady(self):
        """
        This REST endpoint changes the status of a procurement request
        to reflect that its items are ready to be picked up by the students
        who requested them.

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
                {'status': "ordered"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "ready for pickup"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": "marked as ready by admin",
                    "oldState": "ordered",
                    "newState": "ready for pickup"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        # send confirmation email to admin
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'marked as ready for pickup'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'delivered and is ready for pickup',
            'user': cherrypy.session['email'],
            'role': 'admin'
        })


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementComplete(self):
        """
        This REST endpoint changes the status of a procurement request
        to reflect that its items have been picked up and no further
        actions need to be taken.

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
                {'status': "ready for pickup"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "complete"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": "marked as complete by admin",
                    "oldState": "ready for pickup",
                    "newState": "complete"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        # send confirmation email to admin
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'marked as picked up'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudent(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'marked as picked up',
            'user': cherrypy.session['email'],
            'role': 'admin'
        })


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("manager")
    def procurementRejectManager(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request is permanently rejected and unable
        to be further edited or considered by any user.

        Expected input::

            {
                "_id": (string),
                "comment": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # TODO check this action is allowed

        myID = checkValidID(data)
        myComment = checkValidData("comment", data, str)
        if myComment == "":
            myComment = "No comment"
        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "pending"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "rejected"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": myComment,
                    "oldState": "pending",
                    "newState": "rejected"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        # send confirmation email to manager
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'rejected'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudentRejected(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'rejected by your technical manager',
            'user': cherrypy.session['email'],
            'role': 'manager',
            'comment': myComment
        })

        if myRequest['oic'] == 2:
            adminEmails = self.getAdminEmails()
            self.email_handler.notifyRejectedAdmin(**{
                'adminEmails': adminEmails,
                'requestNumber': myRequest['requestNumber'],
                'projectNumber': myRequest['projectNumber'],
                'manager': myRequest['manager']
            })


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def procurementRejectAdmin(self):
        """
        This REST endpoint changes the status of a procurement request
        with the effect that a request is permanently rejected and unable
        to be further edited or considered by any user.

        Expected input::

            {
                "_id": (string),
                "comment": (string)
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myID = checkValidID(data)
        myComment = checkValidData("comment", data, str)
        if myComment == "":
            myComment = "No comment"

        findQuery = {
            '$and': [
                {'_id': ObjectId(myID)},
                {'status': "manager approved"}
            ]}
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "rejected"},
            "$push":
                {"history":
                    {
                    "actor": cherrypy.session["email"],
                    "timestamp": datetime.now(),
                    "comment": myComment,
                    "oldState": "manager approved",
                    "newState": "rejected"
                    }
                }
        }

        self._updateDocument(findQuery, updateQuery, updateRule)

        myRequest = self.colRequests.find_one({'_id': ObjectId(myID)})
        if myRequest is None:
            cherrypy.log("Unable to send email in procurementCancel: missing request with id %s" % myID)
            return

        # send confirmation email to admin
        self.email_handler.confirmRequestManagerAdmin(**{
            'email': cherrypy.session['email'],
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'rejected'
        })

        # send notification emails to students
        teamEmails = self.getTeamEmails(myRequest['projectNumber'])
        self.email_handler.notifyStudentRejected(**{
            'teamEmails': teamEmails,
            'requestNumber': myRequest['requestNumber'],
            'projectNumber': myRequest['projectNumber'],
            'action': 'rejected by an admin',
            'user': cherrypy.session['email'],
            'role': 'admin',
            'comment': myComment
        })


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def getAdminList(self):
        """
        This returns the emails of all admins in the system
        """
        if cherrypy.session['role'] == 'admin':
            results = []
            for res in self.colUsers.find({"role": "admin"}):
                results.append(res["email"])
            return results
        raise cherrypy.HTTPError(400, "Unauthorized access")

    def calculateBudget(self, projectNumber):
        res = list(self.colProjects.find({"projectNumber": projectNumber}))
        if len(res) <= 0:
            raise cherrypy.HTTPError(400, "Invalid project number")

        res = res[0]
        pendingCosts = 0
        actualCosts = 0
        requests = self.colRequests.find({"projectNumber": projectNumber})
        for req in requests:
            if req["status"] in ["admin approved", "ordered", "ready for pickup", "complete"]:
                actualCosts += req.get("requestTotal", 0)
            pendingCosts += req.get("requestTotal", 0)

        miscCosts = 0
        addCosts = self.colCosts.find({"projectNumber": projectNumber})
        for co in addCosts:
            if co["type"] == "refund":
                miscCosts -= co["amount"]
            elif co["type"] == "reimbursement":
                miscCosts += co["amount"]

        res["availableBudget"] = res["defaultBudget"] - actualCosts - miscCosts
        res["pendingBudget"] = res["defaultBudget"] - pendingCosts - miscCosts

        self.colProjects.update_one({"projectNumber": projectNumber}, {"$set": {"availableBudget": res["availableBudget"], "pendingBudget": res["pendingBudget"]}})

        return res

    @cherrypy.expose
    #~ @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def addCost(self):
        """
        This adds a cost (refund, reimbursement, funding, or cut) to a project, and can only be done by the admin
        {
            projectNumber: (int),
            type: (string: refund, reimbursement, new budget),
            amount: (string, dollar amount),
            comment: (string),
            actor: (string, email of admin)
        }
        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        cost = {}

        cost["projectNumber"] = checkValidData("projectNumber", data, int)
        for key in ("type", "amount", "comment", "actor"):
            if key == "type" and data[key] not in ["refund", "reimbursement", "new budget"]:
                print(data[key])
                raise cherrypy.HTTPError(400, "Bad cost type")
            cost[key] = checkValidData(key, data, str)
            if key == "amount":
                cost[key] = lenientConvertToCents(cost[key])
        #~ cost["timestamp"] = datetime.now().isoformat()
        cost["timestamp"] = datetime.now()
        self.colCosts.insert(cost)

        #update the project budget if type == funding or cut
        #~ if cost["type"] == "funding":
            #~ newBudget = list(self.colProjects.find({"projectNumber": cost["projectNumber"]}))[0]["defaultBudget"] + cost["amount"]
            #~ self.colProjects.update_one({"projectNumber": cost["projectNumber"]}, {"$set": {"defaultBudget": newBudget}})
        #~ elif cost["type"] == "cut":
            #~ newBudget = list(self.colProjects.find({"projectNumber": cost["projectNumber"]}))[0]["defaultBudget"] - cost["amount"]
            #~ self.colProjects.update_one({"projectNumber": cost["projectNumber"]}, {"$set": {"defaultBudget": newBudget}})
        if cost["type"] == "new budget":
            self.colProjects.update_one({"projectNumber": cost["projectNumber"]}, {"$set": {"defaultBudget": cost["amount"]}})

        self.calculateBudget(cost["projectNumber"])

        # TODO send confirmation email to admin
        # TODO send notification emails to students

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student", "manager", "admin")
    def getCosts(self):
        """
        This returns all the costs associated with project numbers.
        {
            projectNumbers: (list of ints, optional)
        }
        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = dict()

        validNum = []
        result = []
        if 'projectNumbers' in data:
            # if not admin, find only authorized projects
            if cherrypy.session['role'] == 'admin':
                validNum = data['projectNumbers']
            else:
                for pNum in data['projectNumbers']:
                    if pNum in cherrypy.session['projectNumbers']:
                        validNum.append(pNum)

            for project in validNum:
                for res in self.colCosts.find({'projectNumber': project}):
                    res['_id'] = str(res['_id'])
                    res["timestamp"] = res["timestamp"].isoformat()
                    result.append(res)
            return result
        else:
            if cherrypy.session['role'] != 'admin':
                validNum = cherrypy.session['projectNumbers']
                for project in validNum:
                    for res in self.colCosts.find({'projectNumber': project}):
                        res['_id'] = str(res['_id'])
                        res["timestamp"] = res["timestamp"].isoformat()
                        result.append(res)
                return result
            else:   # is admin
                for res in self.colCosts.find({}):
                    res['_id'] = str(res['_id'])
                    res["timestamp"] = res["timestamp"].isoformat()
                    result.append(res)
                return result

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectAdd(self):
        """
        This adds a project, and can only be done by an admin.
        If the projectNumber is already in use, an error is thrown

        Expected input:
        {
            “projectNumber”: (int),
            “sponsorName”: (string),
            “projectName”: (string),
            “membersEmails: [(string), …], # list of strings
            “defaultBudget”: (string) optional, # TODO not yet optional
            “availableBudget”: (string) optional, # TODO not yet optional
            “pendingBudget”: (string) optional # TODO not yet optional
        }
        """
        # TODO default budget from value in database
        # TODO discuss available and pending budget
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myProject = dict()

        myProject['status'] = 'active'

        for key in ("projectNumber",):
            myProjectNumber = checkValidData(key, data, int)
            query = {"projectNumber": myProjectNumber}
            if self.colProjects.find(query).count() > 0:
                raise cherrypy.HTTPError(400, "project with projectNumber %s already in database" % myProjectNumber)
            else:
                myProject[key] = myProjectNumber

        for key in ("defaultBudget", "availableBudget", "pendingBudget"):
            myProject[key] = checkValidData(key, data, str)
            myProject[key] = lenientConvertToCents(myProject[key])


        for key in ("sponsorName", "projectName"):
            myProject[key] = checkValidData(key, data, str)

        for key in ("membersEmails",):
            emailList = checkValidData(key, data, list)
            newEmailList = []
            for email in emailList:
                if isinstance(email, str):
                    newEmailList.append(email)
                else:
                    raise cherrypy.HTTPError(400, "invalid %s type, emails must be strings" % key)
            myProject[key] = newEmailList

        # insert the data into the database
        self.colProjects.insert(myProject)

        # TODO send confirmation email to admin? maybe not

        # send notification emails to students
        teamEmails = myProject['membersEmails']
        self.email_handler.notifyProjectAdd(**{
            'teamEmails': teamEmails,
            'projectNumber': myProject['projectNumber'],
            'projectName': myProject['projectName']
        })

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectInactivate(self):
        """

        Expected input:
        {
            "_id": (string)
        }
        :return:
        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = dict()

        myID = checkValidID(data)
        findQuery = {'_id': ObjectId(myID)}
        updateRule = {
            "$set":
                {'status': "inactive"}
        }

        self._updateDocument(findQuery, findQuery, updateRule, collection=self.colProjects)

        myProject = self.colProjects.find_one(findQuery)

        # TODO send confirmation to admin who did this

        self.email_handler.notifyProjectInactivate(**{
            'teamEmails': myProject['membersEmails'],
            'projectNumber': myProject['projectNumber'],
            'projectName': myProject['projectName']
        })


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("student", "manager", "admin")
    def findProject(self):
        """
        This finds all projects with the given project numbers and recalculates
        their budget. If none given, then all authorized projects are returned.
        {
            projectNumbers: (list of ints, optional)
        }
        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = dict()

        # TODO validate projectNumbers; verify projectNumbers is list of ints

        validNum = []
        result = []
        if 'projectNumbers' in data:
            # if not admin, find only authorized projects
            if cherrypy.session['role'] == 'admin':
                validNum = data['projectNumbers']
            else:
                for pNum in data['projectNumbers']:
                    if pNum in cherrypy.session['projectNumbers']:
                        validNum.append(pNum)

            for project in validNum:
                for res in self.colProjects.find({'projectNumber': project, 'status': 'active'}):
                    res['_id'] = str(res['_id'])
                    result.append(res)
            #~ return result
        else:
            if cherrypy.session['role'] != 'admin':
                validNum = cherrypy.session['projectNumbers']
                for project in validNum:
                    for res in self.colProjects.find({'projectNumber': project, 'status': 'active'}):
                        res['_id'] = str(res['_id'])
                        result.append(res)
                #~ return result
            else:   # is admin
                for res in self.colProjects.find({'status': 'active'}):
                    res['_id'] = str(res['_id'])
                    result.append(res)
                #~ return result
        '''
        #~ print()
        #~ print("calculating budget")
        #calculate the budget
        for res in result:
            #~ print(res)
            pendingCosts = 0
            actualCosts = 0
            #~ requests = self.procurementStatuses({"projectNumbers": res["projectNumber"]})
            requests = self.colRequests.find({"projectNumber": res["projectNumber"]})
            for req in requests:
                #~ print(req)
                if req["status"] in ["admin approved", "ordered", "ready for pickup", "complete"]:
                    actualCosts += req["requestTotal"]
                pendingCosts += req["requestTotal"]
            #~ print(pendingCosts, actualCosts)

            miscCosts = 0
            addCosts = self.colCosts.find({"projectNumber": res["projectNumber"]})
            for co in addCosts:
                if co["type"] == "refund":
                    miscCosts -= co["amount"]
                elif co["type"] == "reimbursement":
                    miscCosts += co["amount"]
            res["availableBudget"] = res["defaultBudget"] - actualCosts - miscCosts
            res["pendingBudget"] = res["defaultBudget"] - pendingCosts - miscCosts
            #~ print(res)
        #~ print()
        '''

        for res in result:
            res = self.calculateBudget(res["projectNumber"])
        return result

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectEdit(self):
        """
        This changes a project's values. It can only be done by an admin.
        The projectNumber is required, but its value cannot be changed.
        projectNumber is used to specify which project will be edited,
        while the other values are what the values in the database will be set to.
        {
            projectNumber: (int),
            sponsorName: (string, optional),
            projectName: (string, optional),
            membersEmails: [(string), …, optional]
        }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            data = dict()

        myProject = dict()

        for key in ("projectNumber",):
            myProject[key] = checkValidData(key, data, int)

        for key in ("projectName", "sponsorName"):
            myProject[key] = checkValidData(key, data, str)

        for key in ("membersEmails",):
            emailList = checkValidData(key, data, list)
            newEmailList = []
            for email in emailList:
                if isinstance(email, str):
                    newEmailList.append(email)
                else:
                    raise cherrypy.HTTPError(400, "invalid %s type, emails must be strings" % key)
            myProject[key] = newEmailList

        # TODO check projectNumber in database?

        findQuery = {'projectNumber': myProject['projectNumber']}
        updateRule = {
            "$set": {
                'projectName': myProject['projectName'],
                'sponsorName': myProject['sponsorName'],
                'membersEmails': myProject['membersEmails']
            }
        }

        self._updateDocument(findQuery, findQuery, updateRule, collection=self.colProjects)

        # TODO confirmation email to admin maybe
        # TODO notification email to project members maybe
        self.email_handler.notifyProjectEdit(**{
            'membersEmails': myProject['membersEmails'],
            'projectNumber': myProject['projectNumber'],
            'projectName': myProject['projectName'],
            'sponsorName': myProject['sponsorName']
        })


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
        myRole = myRole.lower().strip()
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

        for key in ("firstName", "lastName", "email", "course"):
            myUser[key] = checkValidData(key, data, str)

        if "netID" in myUser:
            myUser['netID'] = checkValidData('netID', data, str)

        # TODO: do something
        emailExisting = self.colUsers.find_one({'email': myUser['email']})
        if emailExisting:
            return # do something

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

        self.email_handler.userAdd(**{
            'email': myInvitation['email'],
            'uuid':  myInvitation['uuid'],
        })

        return {'uuid': myInvitation['uuid']}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def userForgotPassword(self):
        """
        This REST endpoint allows a user to change their password. It
        takes in a user's email address and send that email address a
        recovery link that will expire at some point in the near future.
        This link will allow a user to set a new password through the
        userVerify endpoint.

        Expected input::

            {
                "email": (string),
            }

        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myEmail = checkValidData('email', data, str)

        userDoc = self.colUsers.find_one({'email': myEmail})

        # if no user with this email exists, we don't want to give an adversary
        # the satisfaction of knowing that.
        if not userDoc:
            return

        # create a link (invitation) so the user can set a password
        myInvitation = {
            'uuid': str(uuid4()),
            'expiration': datetime.now() + timedelta(minutes=15),
            'email': myEmail
        }

        self.colInvitations.insert(myInvitation)
        cherrypy.log('Created new invitation. Setup UUID: %s' % myInvitation['uuid'])

        self.email_handler.userForgotPassword(**{
            'email': myInvitation['email'],
            'uuid':  myInvitation['uuid'],
            'expiration': myInvitation['expiration']
        })

        return {'uuid': myInvitation['uuid']}

    @cherrypy.expose
    # @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userSpreadsheetUpload(self, sheet):

        # get the whole file
        xlsx = bytearray()
        while True:
            data = sheet.file.read(8192)
            if not data:
                break
            # size += len(data)
            xlsx.extend(data)

        # parse into pandas dataframe
        df = pd.read_excel(BytesIO(bytes(xlsx)))

        # add each user
        bulkData = {
            'valid': [],
            'invalid': [],
            'existing': [],
            'conflicting': [],
        }
        emailLut = dict()
        for index, row in df.iterrows():
            # get from excel
            myUser = dict()
            if row.size:
                myUser["projectNumbers"] = [int(e) for e in str(row[0]).split()]

            for i, e in enumerate(('firstName', 'lastName', 'netID', 'email', 'course', 'role')):
                i += 1
                if i < row.size:
                    myUser[e] = row[i]
                else:
                    break

            myUser = self.validateUser(myUser, comment=True)

            if 'email' in myUser and myUser['email'] in emailLut:
                # merge this user's project numbers into the old user's project numbers
                # TODO merge courses too
                # TODO maybe check for conflicts?
                prevUser = emailLut[myUser['email']]
                prevUser['projectNumbers'].extend(myUser['projectNumbers'])
                continue
            elif 'email' in myUser:
                emailLut[myUser['email']] = myUser

            if (myUser['comment']['invalidRole'] or
                    myUser['comment']['missingProjects'] or
                    myUser['comment']['missingAttributes'] or
                    myUser['comment']['conflictingAttributes']):
                if myUser['comment']['merge']:
                    bulkData['conflicting'].append(myUser)
                else:
                    bulkData['invalid'].append(myUser)
            else:
                if myUser['comment']['merge']:
                    bulkData['existing'].append(myUser)
                else:
                    bulkData['valid'].append(myUser)

        cherrypy.session['bulkUserData'] = bulkData
        cherrypy.session['bulkUserMetadata'] = {status: len(arr) for status, arr in bulkData.items()}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userSpreadsheetSubmit(self):

        # check that we actually have bulk data
        if 'bulkUserData' in cherrypy.session:
            data = cherrypy.session['bulkUserData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call userSpreadsheetUpload first.')

        # check that all users have been resolved
        if cherrypy.session['bulkUserMetadata']['conflicting'] or cherrypy.session['bulkUserMetadata']['invalid']:
            raise cherrypy.HTTPError(400, 'Not all users have been resolved')

        # invite all new users
        for myUser in data['valid']:
            myInvitation = {
                'uuid': str(uuid4()),
                'expiration': None,
                'email': myUser['email']
            }

            self.colInvitations.insert(myInvitation)
            cherrypy.log('Created new user. Setup UUID: %s' % myInvitation['uuid'])

            self.email_handler.userAdd(**{
                'email': myInvitation['email'],
                'uuid': myInvitation['uuid'],
            })

        # insert all new users
        # TODO once projects can be added, add these users to their projects
        if data['valid']:
            self.colUsers.insert_many(data['valid'])

        # update all existing users
        for myUser in data['existing']:
            oldUser = self.colUsers.find_one({'email': myUser['email']})
            pNumbers = oldUser['projectNumbers'] + myUser['projectNumbers']
            #TODO once course is a list, add courses here too.

            self.colUsers.update_one({
                'email': myUser['email']
            }, {
                '$set': {
                    'projectNumbers': pNumbers
                }
            })

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userSpreadsheetMetadata(self):

        # check that we actually have json
        if 'bulkUserData' in cherrypy.session:
            return cherrypy.session['bulkUserMetadata']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data. Must call userSpreadsheetUpload first.')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userSpreadsheetPages(self):
        """
        Returns an int: the number of pages it would take to
        display all current users if 10 users are displayed
        per page. At present time, the page size (number of
        users per page) cannot be configured.

        {
            "bulkStatus": (string, Optional, default "valid".
                Whether these are the "valid", "invalid", "existing", or
                "conflicting" bulk users)
        }

        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # check that we actually have json
        if 'bulkUserData' in cherrypy.session:
            bulkData = cherrypy.session['bulkUserData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call userSpreadsheetUpload first.')

        pageSize = 10 # TODO stretch goal make this configurable

        div, remainder = divmod(len(bulkData.get(data.get('bulkStatus', 'valid'))), pageSize)
        if remainder:
            return div + 1
        else:
            return div

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userSpreadsheetData(self):
        """
        This REST endpoint returns a list of 10 users from the database. The users may be
        sorted by a key and ordered by ascending or descending, and the pageNumber
        decides which 10 users are returned. pageNumber must be a non-negative integer.

        Incoming ::
        {
            "bulkStatus": (string, Optional, default "valid".
                Whether these are the "valid", "invalid", "existing", or
                "conflicting" bulk users)

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
        if 'bulkUserData' in cherrypy.session:
            bulkData = cherrypy.session['bulkUserData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call userSpreadsheetUpload first.')

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        pageNumber = checkValidData('pageNumber', data, int, default=0,
                                optional=True)

        if pageNumber < 0:
            raise cherrypy.HTTPError(
                400, "Invalid pageNumber format. "
                     "Expected nonnegative integer. "
                     "See: %s" % pageNumber)

        pageSize = 10 # TODO stretch goal make this configurable

        return bulkData[data.get('bulkStatus', 'valid')][pageSize*pageNumber: pageSize*(pageNumber+1)]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userSpreadsheetRevalidate(self):

        # check that we actually have json
        if 'bulkUserData' in cherrypy.session:
            bulkData = cherrypy.session['bulkUserData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call userSpreadsheetUpload first.')

        # check that we actually have bulk data
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myUser = self.validateUser(data.get('user', {}), comment=True)

        myStatus = checkValidData('bulkStatus', data, str)
        if myStatus not in bulkData:
            raise cherrypy.HTTPError(400, "Invalid bulkStatus type: %s" % myStatus)

        myIndex = checkValidData('index', data, int)
        if myIndex < 0 or myIndex >= len(bulkData[myStatus]):
            raise cherrypy.HTTPError(400, "Index %s out of bounds for status: %s" % (myIndex, myStatus))

        newStatus = None
        if (myUser['comment']['invalidRole'] or
                myUser['comment']['missingProjects'] or
                myUser['comment']['missingAttributes'] or
                myUser['comment']['conflictingAttributes']):
            if myUser['comment']['merge']:
                newStatus = 'conflicting'
            else:
                newStatus = 'invalid'
        else:
            if myUser['comment']['merge']:
                newStatus = 'existing'
            else:
                newStatus = 'valid'

        if myStatus != newStatus:
            bulkData[myStatus][myIndex] = None
            bulkData[newStatus].append(myUser)
            cherrypy.session['bulkUserMetadata'][myStatus] -= 1
            cherrypy.session['bulkUserMetadata'][newStatus] += 1

        return {'user': myUser, 'status': newStatus}


    @cherrypy.expose
    # @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectSpreadsheetUpload(self, sheet):

        # get the whole file
        xlsx = bytearray()
        while True:
            data = sheet.file.read(8192)
            if not data:
                break
            # size += len(data)
            xlsx.extend(data)

        # parse into pandas dataframe
        df = pd.read_excel(BytesIO(bytes(xlsx)))

        # validate each project
        bulkData = {
            'valid': [],
            'invalid': [],
            'conflicting': [],
        }
        pnoLut = dict()
        for index, row in df.iterrows():
            # get from excel
            myProject = dict()

            for i, e in enumerate(('projectNumber', 'sponsorName', 'projectName', 'defaultBudget')):
                if i < row.size:
                    myProject[e] = row[i]
                else:
                    break

            # TODO parse numerical and string fields

            myProject = self.validateProject(myProject, comment=True)

            if 'projectNumber' in myProject and myProject['projectNumber'] in pnoLut:
                myProject['comment']['sheetConflict'] = True
                pnoLut[myProject['projectNumber']]['sheetConflict'] = True
                continue
            elif 'projectNumber' in myProject:
                pnoLut[myProject['projectNumber']] = myProject

            if myProject['comment']['existingNumber']:
                bulkData['conflicting'].append(myProject)
            elif (myProject['comment']['sheetConflict'] or
                    myProject['comment']['missingAttributes']):
                bulkData['invalid'].append(myProject)
            else:
                bulkData['valid'].append(myProject)

        cherrypy.session['bulkProjectData'] = bulkData
        cherrypy.session['bulkProjectMetadata'] = {status: len(arr) for status, arr in bulkData.items()}
        cherrypy.session['bulkProjectsOverwrite'] = set()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectSpreadsheetSubmit(self):

        # check that we actually have bulk data
        if 'bulkProjectData' in cherrypy.session:
            data = cherrypy.session['bulkProjectData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call projectSpreadsheetUpload first.')

        # check that all issues have been resolved
        if (cherrypy.session['bulkProjectMetadata']['invalid'] or
                cherrypy.session['bulkProjectMetadata']['conflicting']):
            raise cherrypy.HTTPError(400, 'Not all issues have been resolved')

        # insert all new projects
        operations = []
        for project in data['valid']:
            if project['projectNumber'] in cherrypy.session['bulkProjectsOverwrite']:
                del project['comment']
                operations.append(pm.UpdateOne({'projectNumber': project['projectNumber']}, {'$set': project}))
            else:
                operations.append(pm.InsertOne(project))

        self.colProjects.bulk_write(operations)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def projectSpreadsheetMetadata(self):

        # check that we actually have json
        if 'bulkProjectData' in cherrypy.session:
            return cherrypy.session['bulkProjectMetadata']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data. Must call projectSpreadsheetUpload first.')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def projectSpreadsheetPages(self):
        """
        Returns an int: the number of pages it would take to
        display all current projects if 10 projects are displayed
        per page. At present time, the page size (number of
        projects per page) cannot be configured.

        {
            "bulkStatus": (string, Optional, default "valid".
                Whether these are the "valid", "invalid", or "conflicting")
        }

        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # check that we actually have json
        if 'bulkProjectData' in cherrypy.session:
            bulkData = cherrypy.session['bulkProjectData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call projectSpreadsheetUpload first.')

        pageSize = 10 # TODO stretch goal make this configurable

        div, remainder = divmod(len(bulkData.get(data.get('bulkStatus', 'valid'))), pageSize)
        if remainder:
            return div + 1
        else:
            return div

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def projectSpreadsheetData(self):
        """
        This REST endpoint returns a list of 10 projects from the database. The projects may be
        sorted by a key and ordered by ascending or descending, and the pageNumber
        decides which 10 projects are returned. pageNumber must be a non-negative integer.

        Incoming ::
        {
            "bulkStatus": (string, Optional, default "valid".
                Whether these are the "valid", "invalid", "existing", or
                "conflicting" bulk projects)

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
        if 'bulkProjectData' in cherrypy.session:
            bulkData = cherrypy.session['bulkProjectData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call projectSpreadsheetUpload first.')

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        pageNumber = checkValidData('pageNumber', data, int, default=0,
                                optional=True)

        if pageNumber < 0:
            raise cherrypy.HTTPError(
                400, "Invalid pageNumber format. "
                     "Expected nonnegative integer. "
                     "See: %s" % pageNumber)

        pageSize = 10 # TODO stretch goal make this configurable

        return bulkData[data.get('bulkStatus', 'valid')][pageSize*pageNumber: pageSize*(pageNumber+1)]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectSpreadsheetRevalidate(self):

        # check that we actually have json
        if 'bulkProjectData' in cherrypy.session:
            bulkData = cherrypy.session['bulkProjectData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call projectSpreadsheetUpload first.')

        # check that we actually have bulk data
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myProject = self.validateProject(data.get('project', {}), comment=True)

        myStatus = checkValidData('bulkStatus', data, str)
        if myStatus not in bulkData:
            raise cherrypy.HTTPError(400, "Invalid bulkStatus type: %s" % myStatus)

        myIndex = checkValidData('index', data, int)
        if myIndex < 0 or myIndex >= len(bulkData[myStatus]):
            raise cherrypy.HTTPError(400, "Index %s out of bounds for status: %s" % (myIndex, myStatus))

        newStatus = None
        if myProject['comment']['existingNumber']:
            newStatus = 'conflicting'
        elif (myProject['comment']['sheetConflict'] or
              myProject['comment']['missingAttributes']):
            newStatus = 'invalid'
        else:
            newStatus = 'valid'

        if myStatus != newStatus:
            bulkData[myStatus][myIndex] = None
            bulkData[newStatus].append(myProject)
            cherrypy.session['bulkProjectMetadata'][myStatus] -= 1
            cherrypy.session['bulkProjectMetadata'][newStatus] += 1

        return {'project': myProject, 'status': newStatus}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def projectSpreadsheetOverwrite(self):

        # check that we actually have json
        if 'bulkProjectData' in cherrypy.session:
            bulkData = cherrypy.session['bulkProjectData']
        else:
            raise cherrypy.HTTPError(400, 'No bulk data to add. Must call projectSpreadsheetUpload first.')

        # check that we actually have bulk data
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myPno = checkValidData('projectNumber', data, int, coerce=True)
        cherrypy.session['bulkProjectsOverwrite'].add(myPno)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userEdit(self):
        """
        This REST endpoint edits a user document in the databse. It takes a
        MongoDB ObjectID and optional data fields for a user. The ObjectID is
        used to identify the user whose information will be edited and the
        optional data provided to the endpoint is what the existing data will
        be changed to.

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
            myData['projectNumbers'] = checkProjectNumbers(data)

        # optional keys, string
        for key in ("firstName", "lastName", "netID", "course"):
            if key in data:
                myData[key] = checkValidData(key, data, str)

        # update the document
        updateQuery = {'_id': ObjectId(myID)}
        updateRule = {'$set': myData}
        self._updateDocument(updateQuery, updateQuery, updateRule, collection=self.colUsers)

        myUser = self.colUsers.find_one({'_id': ObjectId(myID)})


        # TODO what if user doesn't have netID or course?
        # TODO separate templates for notifying students or managers or admin?
        self.email_handler.notifyUserEdit(**{
            'email': myUser['email'],
            'projectNumbers': myUser['projectNumbers'],
            'firstName': myUser['firstName'],
            'lastName': myUser['lastName'],
            'netID': myUser['netID'],
            'course': myUser['course']

        })

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @authorizedRoles("admin")
    def userRemove(self):
        """
        This REST endpoint "removes" a user from the system. It changes the
        status of a user with the effect that the user is no longer able to
        interact with the system, but doesn't delete their data from the database.

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

        self._updateDocument(findQuery, updateQuery, updateRule, collection=self.colUsers)

        myUser = self.colUsers.find_one(findQuery)

        # TODO send confirmation email to admin?

        self.email_handler.notifyUserRemove(**{
            'email': myUser['email'],
            'firstName': myUser['firstName'],
            'lastName': myUser['lastName']
        })

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def userVerify(self):
        """
        This REST endpoint allows a new user to set their password.
        It checks that a provided email is matched with a provided UUID.
        If so, it creates and stores a password hash and salt for the user.
        The UUID is a key in an invitation document. The document is created
        when a user is first invited to use the system and when a user
        forgets their password.

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

        cherrypy.log("Email: %s. Invitation: %s. UUID: %s" % (data['email'], invitation, myData['uuid']))

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

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def userLogin(self):
        """
        This REST endpoint takes an email and password, checks if the password's hash
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
    @cherrypy.tools.json_in()
    def projectValidate(self):
        """
        Returns true if the project number(s) exist in the database

        Returns ::
            {
                "valid": boolean
            }
        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myData = dict()

        myData["projectNums"] = checkProjectNumbers(data)

        for p in myData["projectNums"]:
            if not bool(self.colProjects.find_one({'projectNumber': p})):
                return 'false'
        return 'true'



    # TODO should this be a rest endpoint?
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
    # NOTE we can use this as a welcome screen; ie "Welcome User". This can also be used to set some default values (ie project number, email)
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
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def projectPages(self):
        """
        Returns an int: the number of pages it would take to
        display all current projects if 10 projects are displayed
        per page. At present time, the page size (number of
        projects per page) cannot be configured.

        {
            "projectNumber": (int),
            "sponsorName": (string, optional),
            "projectName": (string, optional),
            "membersEmails": (string, optional),
            "defaultBudget": (string, optional)
        }

        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            myFilter = getProjectKeywords(cherrypy.request.json)
        else:
            myFilter = getProjectKeywords()
        #myFilter['status'] = 'current'

        pageSize = 10 # TODO stretch goal make this configurable

        div, remainder = divmod(self.colProjects.find(myFilter).count(), pageSize)
        if remainder:
            return div + 1
        else:
            return div

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userPages(self):
        """
        Returns an int: the number of pages it would take to
        display all current users if 10 users are displayed
        per page. At present time, the page size (number of
        users per page) cannot be configured.

        {
            "projectNumbers": (int or list of ints, optional),
            "firstName": (string, optional),
            "lastName": (string, optional),
            "netID": (string, optional),
            "email": (string, optional),
            "course": (string, optional),
            "role": (string, optional)
        }

        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            myFilter = getKeywords(cherrypy.request.json)
        else:
            myFilter = dict()
        myFilter['status'] = 'current'

        pageSize = 10 # TODO stretch goal make this configurable

        div, remainder = divmod(self.colUsers.find(myFilter).count(), pageSize)
        if remainder:
            return div + 1
        else:
            return div

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def requestPages(self):
        """

        {
            primaryFilter: {
            },
            secondaryFilter: {
            }
        }

        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            myFilter = getRequestKeywords(cherrypy.request.json)
        else:
            myFilter = dict()

        pageSize = 10 # TODO stretch goal make this configurable

        div, remainder = divmod(self.colRequests.find(myFilter).count(), pageSize)
        if remainder:
            return div + 1
        else:
            return div


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def requestData(self):
        """
        This REST endpoint returns a list of 10 users from the database. The users may be
        sorted by a key and ordered by ascending or descending, and the pageNumber
        decides which 10 users are returned. pageNumber must be a non-negative integer.

        Incoming ::
        {
            'sortBy': (string in projectNumbers, firstName, lastName, netID,
                email, course, role, status)
                (Optional. Default "email")
            'order': (string in 'ascending', 'descending')
                (Optional. Default: "ascending")
            'pageNumber': (int)
                (Optional. Default: 0)
            'keywordSearch': (dict)
                {
                    primaryFilter: {
                    },
                    secondaryFilter: {
                    }
                }
        }

        Outgoing ::

        """
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # prepare the sort, order, and page number
        sortBy = checkValidData('sortBy', data, str, default='requestNumber',
                                optional=True)

        keyList = ('requestNumber', 'projectNumber', 'status', 'vendor', 'URL', 'requestTotal', 'shippingCost')
        if sortBy not in keyList:
            raise cherrypy.HTTPError(400, 'sortBy must be any of %s. Not %s' % (', '.join(keyList), sortBy))

        order = checkValidData('order', data, str, default='ascending',
                                optional=True)

        if order not in ('ascending', 'descending'):
            raise cherrypy.HTTPError(
                400, 'order must be ascending or descending. Not %s.' % order)

        direction = pm.ASCENDING if order == 'ascending' else pm.DESCENDING

        pageNumber = checkValidData('pageNumber', data, int, default=0,
                                optional=True)

        if pageNumber < 0:
            raise cherrypy.HTTPError(
                400, "Invalid pageNumber format. "
                     "Expected nonnegative integer. "
                     "See: %s" % pageNumber)

        pageSize = 10 # TODO stretch goal make this configurable

        myFilter = getRequestKeywords(data)

        # finds users who are current only
        cursor = self.colRequests.find(myFilter).collation({ 'locale': 'en' }).sort(sortBy, direction)

        retUsers = []
        for request in cursor[pageSize*pageNumber: pageSize*(pageNumber+1)]:
            request['_id'] = str(request['_id'])
            if 'history' in request:
                for hist in range(len(request['history'])):
                    if 'timestamp' in request['history'][hist]:
                        request['history'][hist]['timestamp'] = request['history'][hist]['timestamp'].isoformat(' ')[0:16]
            retUsers.append(request)

        return retUsers

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def projectData(self):
        """
        This REST endpoint returns a list of 10 projects from the database. The projects may be
        sorted by a key and ordered by ascending or descending, and the pageNumber
        decides which 10 projects are returned. pageNumber must be a non-negative integer.

        Incoming ::
        {
            'sortBy': (string in projectNumber, sponsorName, projectName, membersEmails,
                defaultBudget)
                (Optional. Default "projectNumber")
            'order': (string in 'ascending', 'descending')
                (Optional. Default: "ascending")
            'pageNumber': (int)
                (Optional. Default: 0)
            'keywordSearch': (dict)
                {
                    "projectNumber": (int, optional),
                    "sponsorName": (string, optional),
                    "projectName": (string, optional),
                    "membersEmails": (string, optional),
                    "defaultBudget": (string, optional)
                }
        }

        Outgoing ::
        [
            {
                “projectNumber”: (int),
                "sponsorName": (string),
                "projectName": (string),
                "membersEmails": (string),
                "defaultBudget": (string)
            }
        ]

        """

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # prepare the sort, order, and page number
        sortBy = checkValidData('sortBy', data, str, default='projectNumber',
                                optional=True)

        if sortBy not in ('projectNumber', 'sponsorName', 'projectName', 'membersEmails', 'defaultBudget'):
            raise cherrypy.HTTPError(
                400, 'sortBy must be any of projectNumber, sponsorName, projectName, membersEmails, defaultBudget. Not %s'
                     % sortBy)

        order = checkValidData('order', data, str, default='ascending',
                                optional=True)

        if order not in ('ascending', 'descending'):
            raise cherrypy.HTTPError(
                400, 'order must be ascending or descending. Not %s.' % order)

        direction = pm.ASCENDING if order == 'ascending' else pm.DESCENDING

        pageNumber = checkValidData('pageNumber', data, int, default=0,
                                optional=True)

        if pageNumber < 0:
            raise cherrypy.HTTPError(
                400, "Invalid pageNumber format. "
                     "Expected nonnegative integer. "
                     "See: %s" % pageNumber)

        pageSize = 10 # TODO stretch goal make this configurable

        myFilter = getProjectKeywords(data.get('keywordSearch', {}))
        #myFilter['status'] = 'current'

        # finds projects who are current only
        projectCursor = self.colProjects.find(myFilter).collation({ 'locale': 'en' }).sort(sortBy, direction)

        retProjects = []
        for proj in projectCursor[pageSize*pageNumber: pageSize*(pageNumber+1)]:
            myProj = dict()
            myProj['_id'] = str(proj['_id'])
            for key in ('sponsorName', 'projectName', 'membersEmails', 'defaultBudget'):
                myProj[key] = proj.get(key, '')

            myProj['projectNumber'] = proj.get('projectNumber', '')

            # if myUser['role'] != 'admin':
            #     for key in ('projectNumbers', 'course'):
            #         myUser[key] = user[key]

            retProjects.append(myProj)


        return retProjects

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userSingleData(self):
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myEmail = checkValidData('email', data, str)
        user = self.colUsers.find_one({'email': myEmail})
        if user:
            myUser = dict()
            for key in ("projectNumbers", "firstName", "lastName", "netID", "course", 'email', 'role'):
                myUser[key] = user[key]
            return myUser
        else:
            return dict()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def projectSingleData(self):
        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        myPno = checkValidData('projectNumber', data, int, coerce=True)
        project = self.colProjects.find_one({'projectNumber': myPno})
        if project:
            myProject = dict()
            for key in ("projectNumber", "sponsorName", "projectName", "defaultBudget", "membersEmails"):
                if key in project:
                    myProject[key] = project[key]
            return myProject
        else:
            return dict()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def userData(self):
        """
        This REST endpoint returns a list of 10 users from the database. The users may be
        sorted by a key and ordered by ascending or descending, and the pageNumber
        decides which 10 users are returned. pageNumber must be a non-negative integer.

        Incoming ::
        {
            'sortBy': (string in projectNumbers, firstName, lastName, netID,
                email, course, role, status)
                (Optional. Default "email")
            'order': (string in 'ascending', 'descending')
                (Optional. Default: "ascending")
            'pageNumber': (int)
                (Optional. Default: 0)
            'keywordSearch': (dict)
                {
                    "projectNumbers": (int or list of ints, optional),
                    "firstName": (string, optional),
                    "lastName": (string, optional),
                    "netID": (string, optional),
                    "email": (string, optional),
                    "course": (string, optional),
                    "role": (string, optional)
                }
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

        # prepare the sort, order, and page number
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

        if pageNumber < 0:
            raise cherrypy.HTTPError(
                400, "Invalid pageNumber format. "
                     "Expected nonnegative integer. "
                     "See: %s" % pageNumber)

        pageSize = 10 # TODO stretch goal make this configurable

        if 'keywordSearch' in data:
            myFilter = getKeywords(data['keywordSearch'])
        else:
            myFilter = dict()
        myFilter['status'] = 'current'

        # finds users who are current only
        userCursor = self.colUsers.find(myFilter).collation({ 'locale': 'en' }).sort(sortBy, direction)

        retUsers = []
        for user in userCursor[pageSize*pageNumber: pageSize*(pageNumber+1)]:
            myUser = dict()
            myUser['_id'] = str(user['_id'])
            for key in ('firstName', 'lastName', 'email', 'status', 'role'):
                myUser[key] = user.get(key, '')

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

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authorizedRoles("admin")
    def reportGenerate(self):

        # check that we actually have json
        if hasattr(cherrypy.request, 'json'):
            data = cherrypy.request.json
        else:
            raise cherrypy.HTTPError(400, 'No data was given')

        # prepare the sort, order, and page number
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

        myFilter = getRequestKeywords(data)

        cursor = self.colRequests.find(myFilter).sort(sortBy, direction)

        # generate the report
        fieldKeys = ["requestNumber", "projectNumber", "status", "vendor", "URL", "requestTotal", "shippingCost"]
        fields = ["Request Number", "Project Number", "Status", "Vendor", "URL", "Total Cost", "Shipping Cost"]
        itemFieldKeys = ["description", 'itemURL', "partNo", "quantity", "unitCost", "totalCost"]
        itemFields = ["Description", 'Item URL', "Catalog Part Number", "Quantity", "Estimated Unit Cost", "Total Cost"]

        uuid = str(uuid4())
        filename = uuid + '.xlsx'
        workbook = xlsxwriter.Workbook(filename)
        for request in cursor:
            # every report has its own sheet
            worksheet = workbook.add_worksheet()

            # headers
            for colIdx, field in enumerate(fields):
                coordinate = chr(ord('A') + colIdx)
                worksheet.write(coordinate + '1', field)
                worksheet.write(coordinate + '2', request.get(fieldKeys[colIdx]), '')

            for colIdx, itemField in enumerate(itemFields):
                coordinate = chr(ord('A') + colIdx)
                worksheet.write(coordinate + '4', itemField)

            # items
            for rowIdx, item in enumerate(request['items']):
                for colIdx, itemField in enumerate(itemFields):
                    coordinate = chr(ord('A') + colIdx)
                    worksheet.write('%s%d' % (coordinate, rowIdx+5), item.get(itemFieldKeys[colIdx], ''))

        workbook.close()

        self.reportUUIDs.append(uuid)

        return uuid

    @cherrypy.expose
    # @authorizedRoles("admin")
    def reportDownload(self, uuid):
        # check that we actually have json
        if uuid in self.reportUUIDs:
            filename = uuid + '.xlsx'
            path = os.path.join(absDir, filename)
            return cherrypy.lib.static.serve_file(path, 'application/x-download',
                                           'attachment', os.path.basename(path))
        else:
            raise cherrypy.HTTPError(404, "No such file.")

    # helper function, do not expose!
    def _updateDocument(self, findQuery, updateQuery, updateRule, collection=None):
        """
        This function updates a document. It finds the document in the
        database and updates it using the provided queries/rules.

        :param myID: ID of document to be updated
        :param findQuery: query to find document
        :param updateQuery: query to find document to update
        :param updateRule: rule to update document to update
        """

        if collection is None:
            collection = self.colRequests
        if collection.find(findQuery).count() > 0:
            collection.update_one(updateQuery, updateRule, upsert=False)
        else:
            raise cherrypy.HTTPError(
                400, 'Request matching id and status not found in database')

    # helper function, do not expose!
    # TODO edge cases?
    def getTeamEmails(self, projectNumber):
        teamEmails = []
        for user in self.colUsers.find({'projectNumbers': projectNumber}):
            if user['role'] == 'student':
                teamEmails.append(user['email'])
        return teamEmails

    #helper function, do not expose
    # TODO check if redundant (getAdminList)
    def getAdminEmails(self):
        adminEmails = []
        for user in self.colUsers.find({'role': 'admin'}):
            adminEmails.append(user['email'])
        return adminEmails

    #helper function, do not expose
    def validateUser(self, data, comment=False):
        """
        Validates a user to check for a role, firstName, lastName, email,
        and optional netID. Non-admin users are also checked for valid
        project numbers and courses.

        A sanitized version of the user dict is returned, or None if anything
        was wrong with the dict.

        If comment is True, then the user also has a 'comment' attribute ::

            comment: {
                merge: (boolean, if a user with this email exists),
                invalidRole: (boolean)
                missingProjects: (list of ints)
                missingAttributes: (list of strings)
                conflictingAttributes: (list of strings),
            }

        :param data: dict. The user to be validated.
        :param myComment: bool. As described above.
        :return:
        """

        myComment = {
            'merge': False,
            'invalidRole': False,
            'missingProjects': [],
            'missingAttributes': [],
            'conflictingAttributes': [],
        }

        myUser = dict()

        # set default value of value in dict
        myUser['status'] = 'current'

        # get the user's role
        try:
            myRole = checkValidData("role", data, str)
        except cherrypy.HTTPError:
            if comment:
                myComment['missingAttributes'].append("role")
                myRole = None
            else:
                return None

        # check the user's role
        if myRole is not None:
            myRole = myRole.lower().strip()
            if myRole in ("student", "manager", "admin"):
                myUser['role'] = myRole
            elif myRole:
                if comment:
                    myComment['invalidRole'] = True
                else:
                    return None

        # check the user's project number and course
        if myRole != 'admin':
            try:
                myUser['projectNumbers'] = checkProjectNumbers(data)
            except cherrypy.HTTPError:
                if comment:
                    myComment['missingAttributes'].append("projectNumbers")
                else:
                    return None

            try:
                myUser['course'] = checkValidData('course', data, str)
            except cherrypy.HTTPError:
                if comment:
                    myComment['missingAttributes'].append("course")
                else:
                    return None

        # check the users other keys
        for key in ("firstName", "lastName", "email"):
            try:
                myUser[key] = checkValidData(key, data, str)
            except cherrypy.HTTPError:
                if comment:
                    myComment['missingAttributes'].append(key)
                else:
                    return None

        # get the netID if any
        if "netID" in data:
            myUser['netID'] = str(data['netID'])

        if comment:
            # check for merging and conflicts
            if 'email' in myUser:
                oldUser = self.colUsers.find_one({'email': myUser['email']})
                if oldUser:
                    myComment['merge'] = True
                    for key in ('role', 'firstName', 'lastName', 'email', 'netID'):
                        if myUser.get(key, None) != oldUser[key]:
                            myComment['conflictingAttributes'].append(key)

            # check for valid project
            if 'projectNumbers' in myUser:
                for projectNumber in myUser['projectNumbers']:
                    if not self.colProjects.find_one({'projectNumber': projectNumber}):
                        myComment['missingProjects'].append(projectNumber)

        if comment:
            myUser['comment'] = myComment
        return myUser

    #helper function, do not expose
    def validateProject(self, data, comment=False):
        """
        Validates a project to check for a projectNumber, sponsorName, projectName,
        memberEmails, and defaultBudget. If types are wrong, things are coerced
        if possible.

        A sanitized version of the project dict is returned.

        If comment is True, then the project also has a 'comment' attribute ::

            comment: {
                missingAttributes: (list of strings)
                existingNumber: (boolean, true if a project with this projectNumber exists),
            }

        :param data: dict. The project to be validated.
        :param myComment: bool. As described above.
        :return:
        """

        myComment = {
            'sheetConflict': False,
            'existingNumber': False,
            'missingAttributes': [],
        }

        myProject = dict()

        # set default value of value in dict
        myProject['status'] = 'active'

        # get the projectNumber
        try:
            myProject['projectNumber'] = checkValidData("projectNumber", data, int, coerce=True)

            if myProject['projectNumber'] not in cherrypy.session.get('bulkProjectsOverwrite', tuple()):
                oldProject = self.colProjects.find_one({'projectNumber': myProject['projectNumber']})
                if oldProject:
                    myComment['existingNumber'] = True

        except cherrypy.HTTPError:
            if comment:
                myComment['missingAttributes'].append("projectNumber")
            else:
                return None

        # get the defaultBudget
        try:
            myCurrency = checkValidData("defaultBudget", data, str, coerce=True)
            myProject['defaultBudget'] = lenientConvertToCents(myCurrency)
        except cherrypy.HTTPError:
            if comment:
                myComment['missingAttributes'].append("defaultBudget")
            else:
                return None

        # check the project's other keys
        for key in ("sponsorName", "projectName"):
            try:
                myProject[key] = checkValidData(key, data, str)
            except cherrypy.HTTPError:
                if comment:
                    myComment['missingAttributes'].append(key)
                else:
                    return None

        if comment:
            myProject['comment'] = myComment
        return myProject

