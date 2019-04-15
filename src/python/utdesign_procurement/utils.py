#!/usr/bin/env python3

import cherrypy
import hashlib
import os
import re

from bson.objectid import ObjectId

def authorizedRoles(*acceptableRoles, redirect=False):
    """
    This is a decorator factory which checks the role of a user by their
    session information. If their role is not in the given list of
    authorized roles, then they are denied access.

    If redirect=True, and the user isn't logged in at all, then they are
    redirected to the login page. If redirect=False (default), then they
    are denied access with a 403 error.
    """

    def decorator(func):

        def decorated_function(*args, **kwargs):
            role = cherrypy.session.get('role', None)

            # cherrypy.log("authorizedRoles called with user role %s and "
            #              "roles %s" % (role, acceptableRoles))

            # no role means force a login
            if role is None and redirect:
                raise cherrypy.HTTPRedirect('/login')

            # not authorized means raise hell!
            if role not in acceptableRoles:
                raise cherrypy.HTTPError(403)

            # by now, they're surely authorized
            return func(*args, **kwargs)

        return decorated_function

    return decorator

def verifyPassword(user, password):
    """
    This function hashes a password and checks if it matches the hash of
    a given user.

    :param user: a user document from database
    :param password: a hashed password
    """

    # user['password'] is hashed password, not plaintext
    # code assumes salt and password are type checked?
    if user and 'salt' in user and 'password' in user:
        return user['password'] == hashPassword(password, user['salt'])
    else:
        return False

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

def generateSalt():
    """
    This function generates a random salt.

    :return: random salt
    """
    # create 32 byte salt (note: changed from 8)
    # string of random bytes
    # platform-specific (windows uses CryptGenRandom())
    return os.urandom(32)

def checkProjectNumbers(data, default=None):
    """
    Return a list of project numbers from the given dict if possible.
    If not found, return a default value if given, else raise a 400 error.

    :param data: The dict from which to obtain project numbers
    :param default: A default value to return if no project numbers are
        found.
    :return:
    """
    if 'projectNumbers' in data:
        myPNo = data['projectNumbers']
        if isinstance(myPNo, int):
            myPNo = [myPNo]

        if all(isinstance(pNo, int) for pNo in myPNo):
            return myPNo
        else:
            raise cherrypy.HTTPError(
                400, 'Expected project number to be int or list of int.'
                     'See: %s' % myPNo)
    elif default:
        return default
    else:
        raise cherrypy.HTTPError(400, 'Project Number not found.')

# checks if key value exists and is the right type
def checkValidData(key, data, dataType, optional=False, default=""):
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
            cherrypy.log("Expected %s of type %s. See: %s" %
            (key, dataType, localVar))
            raise cherrypy.HTTPError(400, 'Invalid %s format. See: %s' % (key, data[key]))
    else:
        if not optional:
            raise cherrypy.HTTPError(400, 'Missing %s' % key)
        else:
            return default

# checks if key value exists and is the right type (Number)
def checkValidNumber(key, data, optional=False, default=""):
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
            cherrypy.log(
                "Expected %s to be a number. See: %s" % (key, localVar))
            raise cherrypy.HTTPError(400, 'Invalid %s format' % key)
    else:
        if not optional:
            raise cherrypy.HTTPError(400, 'Missing %s' % key)
        else:
            return default

# checks if data has valid object ID
def checkValidID(data):
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

def convertToCents(dollarAmt):
    """
    Converts a string dollar amount to an int cents amount
    :param dollarAmt: the string dollar amount, does not have $ sign
    :return: cents in int
    """
    try:
        #~ "{:.2f}".format(float(dollarAmt))
        #~ if re.match("^[0-9]*(?:\.[0-9]{2})?$", dollarAmt):
        if re.match("^[0-9]*\.[0-9]{2}?$", dollarAmt):
            return int(dollarAmt.replace(".", ""))
        else:
            raise cherrypy.HTTPError(400, "Bad currency value")
    except:
        raise cherrypy.HTTPError(400, "Bad currency value")

def lenientConvertToCents(dollarAmt):
    """
    Converts a string dollar amount to an int cents amount
    :param dollarAmt: the string dollar amount, does not have $ sign
    :return: cents in int
    """
    try:
        if re.match("^[0-9]*\.[0-9]{2}?$", dollarAmt):
            return int(dollarAmt.replace(".", ""))
        elif re.match("^[0-9]+$", dollarAmt):
            return int(dollarAmt) * 100
        else:
            raise cherrypy.HTTPError(400, "Bad currency value")
    except:
        raise cherrypy.HTTPError(400, "Bad currency value")

def requestCreate(data, status, optional=False):
    """
    Takes data as an input as uses the data to create
    a procurement request (dict).

    Expected input::

        {
            "manager": (string), //email of manager who can approve this
            "vendor": (string),
            "projectNumber": (int or list of int),
            "URL": (string),
            "justification": (string) optional,
            "additionalInfo": (string) optional,
            "items": [
                {
                "description": (string),
                "partNo": (string),
                "itemURL": (string),
                "quantity": (int),
                "unitCost": (string),
                "totalCost": (string)
                }
            ]
        }
    :param data: a dict containing data to be stored in the request
    :param status: what will be the initial status of the request?
    :param optional: if True, all fields of data except procjectNumber will be optional
    :return: procurement request, stored as a dict
    """
    myRequest = dict()

    myRequest['status'] = status

    # mandatory projectNumber
    for key in ("projectNumber",):
        myRequest[key] = checkValidData(key, data, int) #not optional ever

    # mandatory keys (unless optional is True)
    for key in ("manager", "vendor", "URL"):
        myRequest[key] = checkValidData(key, data, str, optional)
    # TODO check valid manager (is submitted to correct manager for project, check that email exists)

    # always optional keys
    for key in ("justification", "additionalInfo"):
        myRequest[key] = checkValidData(key, data, str, True)

    # theirItems is a list of dicts (each dict is one item)
    theirItems = checkValidData("items", data, list, optional)

    # myItems is the list we are creating and adding to the database
    myItems = []

    requestSubtotal = 0

    # iterate through list of items
    for theirDict in theirItems:
        # theirDict = checkValidData(item, data, dict) #check dict is actually a dict?
        myDict = dict()
        # iterate through keys of item dict
        for key in ("description", "partNo", "itemURL", "unitCost"):
            myDict[key] = checkValidData(key, theirDict, str, optional)
        for key in ("quantity",):
            myDict[key] = checkValidData(key, theirDict, int, optional)
        myDict['totalCost'] = checkValidData("totalCost", theirDict, str, optional)

        # TODO check
        # TODO convert cost strings to ints of cents

        #convert unitCost and totalCost to cents, and calculate the subTotal
        for key in ("unitCost", "totalCost"):
            myDict[key] = convertToCents(myDict[key])
        requestSubtotal += myDict["totalCost"]
        
        myItems.append(myDict)

    myRequest["items"] = myItems
    myRequest["requestSubtotal"] = requestSubtotal

    #since this is creating a request, the shipping cost will be 0 (not set yet) and the requestTotal will be the same as requestSubtotal
    myRequest["requestTotal"] = requestSubtotal

    return myRequest

def getKeywords(keywords):
    # TODO rename this to be getUserKeywords
    # parse the keyword search
    myFilter = dict()

    cherrypy.log(str(keywords))

    for kw in ('projectNumbers', 'firstName', 'lastName', 'netID', 'email', 'course', 'role'):
        if kw in keywords:
            s = checkValidData(kw, keywords, str).strip()
            if s:
                myFilter[kw] = {
                    '$regex': re.compile('.*' + re.escape(s) + '.*', re.IGNORECASE)
                }

    # parse out proper project numbers
    if 'projectNumbers' in myFilter:
        try:
            myFilter['projectNumbers'] = {'$in': list(
                map(int, keywords['projectNumbers'].split()))}
        except ValueError:
            raise cherrypy.HTTPError(400, 'Invalid projectNumbers format')

    # parse out proper role
    if 'role' in keywords:
        role = keywords['role']
        if role in ('student', 'manager', 'admin'):
            myFilter['role'] = role
        else:
            raise cherrypy.HTTPError(400, 'Invalid role. See: %s' % role)

    return myFilter


def getProjectKeywords(keywords):
    # parse the keyword search
    myFilter = {'status': 'active'}

    for kw in ('projectNumber', 'projectName', 'sponsorName', 'membersEmails'):
        if kw in keywords:
            s = checkValidData(kw, keywords, str).strip()
            if s:
                myFilter[kw] = {
                    '$regex': re.compile('.*' + re.escape(s) + '.*', re.IGNORECASE)
                }

    # parse out proper project numbers
    if 'projectNumber' in myFilter:
        try:
            myFilter['projectNumber'] = {'$in': list(
                map(int, keywords['projectNumber'].split()))}
        except ValueError:
            raise cherrypy.HTTPError(400, 'Invalid projectNumber format')

    if 'defaultBudget' in keywords:
        s = keywords['defaultBudget'].strip()
        if s:
            try:
                myFilter['defaultBudget'] = convertToCents(s)
            except cherrypy.HTTPError:
                cherrypy.log('sadness c : ::%s::' % s)

        else:
            cherrypy.log('sadness b : ::%s::' % s)

    else:
        cherrypy.log('sadness a')

    return myFilter