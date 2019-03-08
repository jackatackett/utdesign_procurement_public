#!/usr/bin/env python3

import cherrypy
import hashlib
import os

from bson.objectid import ObjectId

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
            raise cherrypy.HTTPError(400, 'Invalid %s format' % key)
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

def requestCreate(data, status, optional=False):
    """
    Takes data as an input as uses the data to create
    a procurement request (dict).

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
    :param data: a dict containing data to be stored in the request
    :param status: what will be the initial status of the request?
    :param optional: if True, all fields of data will be optional
    :return: procurement request, stored as a dict
    """
    myRequest = dict()

    myRequest['status'] = status

    # mandatory projectNumber
    myRequest['projectNumber'] = checkValidData('projectNumber', data, int, optional)

    # mandatory keys (unless optional is True)
    for key in ("vendor", "URL"):
        myRequest[key] = checkValidData(key, data, str, optional)

    # always optional keys
    for key in ("justification", "additionalInfo"):
        myRequest[key] = checkValidData(key, data, str, True)

    # theirItems is a list of dicts (each dict is one item)
    theirItems = checkValidData("items", data, list, optional)

    # myItems is the list we are creating and adding to the database
    myItems = []

    # iterate through list of items
    for theirDict in theirItems:
        # theirDict = checkValidData(item, data, dict) #check dict is actually a dict?
        myDict = dict()
        # iterate through keys of item dict
        for key in ("description", "partNo", "quantity", "unitCost"):
            myDict[key] = checkValidData(key, theirDict, str, optional)
        myDict['totalCost'] = checkValidNumber("totalCost", theirDict, optional)
        myItems.append(myDict)

    myRequest["items"] = myItems

    return myRequest