#!/usr/bin/env python3

import pymongo as pm
import json
import requests

from unittest import TestCase

class LoginTester(TestCase):
    """
    Tests the user login sequence of events.

    This class will try to log in as an admin, add a new user, verify the
    user account and set a password, and try to log in as that user.
    """

    def test_login(self):
        """
        Test the user login sequence of events.

        :return:
        """

        # get domain
        self.domain = 'http://localhost:8080'

        # connect to MongoDB
        client = pm.MongoClient()
        db = client['procurement']
        self.colUsers = db['users']
        self.colInvitations = db['invitations']

        # find an unused email address
        email = 'randomchump@utdallas.edu'
        while self.colUsers.find_one({'email': email}):
            email = 'very' + email
        unusedEmail = email


        cookies = self.do_admin_login()
        uuid = self.do_user_add(cookies, unusedEmail)
        self.do_user_verify(uuid, unusedEmail)
        self.do_chump_login(unusedEmail)

    def do_admin_login(self):
        """
        Login as the admin.
        Test the /userLogin REST endpoint.

        :return: CookieJar. The cookies returned by /userLogin
        """

        # send our user to be created
        response = requests.post(
            '%s/userLogin' % self.domain,
            headers = {
                'Content-type': 'application/json'
            },
            data = json.dumps({
                "email": "admin@utdallas.edu",
                "password": "oddrun",
            })
        )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # save our cookies for later
        return response.cookies

    def do_user_add(self, cookies, email):
        """
        Test the /userAdd REST endpoint.
        This requires being logged in as an admin.

        :param cookies: CookieJar. A valid admin session id.
        :param email: str. The email address of the user to be added.

        :return: str. The uuid of the invitation returned
        """

        # send our user to be created
        response = requests.post(
            '%s/userAdd' % self.domain,
            cookies = cookies,
            headers = {
                'Content-type': 'application/json'
            },
            data = json.dumps({
                "projectNumbers": [1],
                "firstName": "Random",
                "lastName": "Chump",
                "netID": "rxc123456",
                "email": email,
                "course": "CS 4485.001",
                "role": "student"
            }),
        )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # save the uuid
        j = json.loads(response.content.decode('utf-8'))
        self.assertIn('uuid', j)
        uuid = j['uuid']

        # see if his user data is in MongoDB now
        postCondition = {
            "course": "CS 4485.001",
            "projectNumbers": [1],
            "email": email,
            "status": "current",
            "role": "student",
            "firstName": "Random",
            "lastName": "Chump",
        }

        userDoc = self.colUsers.find_one({"email": email})
        for key, val in postCondition.items():
            self.assertIn(key, userDoc)
            self.assertEqual(val, userDoc[key])

        # see if his invitation is in MongoDB now
        inviteDoc = self.colInvitations.find_one({"uuid": uuid})
        self.assertTrue(inviteDoc)
        self.assertIn("email", inviteDoc)
        self.assertEqual(email, userDoc['email'])

        return uuid

    def do_user_verify(self, uuid, email):
        """
        Test the /userVerify REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        # set our password
        response = requests.post(
            '%s/userVerify' % self.domain,
            headers = {
                'Content-type': 'application/json'
            },
            data = json.dumps({
                "email": email,
                "uuid": uuid,
                "password": "oddrun"
            }),
        )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # see if his user data has some password hash in MongoDB now
        userDoc = self.colUsers.find_one({"email": email})
        self.assertIn('password', userDoc)


    def do_chump_login(self, email):
        """
        Login as the new student.
        Test the validity of the /userVerify and /userLogin REST endpoints.

        :param email: str. The email address of the user to be added.
        :return: CookieJar. The cookies returned by /userLogin
        """

        # send our user to be created
        response = requests.post(
            '%s/userLogin' % self.domain,
            headers = {
                'Content-type': 'application/json'
            },
            data = json.dumps({
                "email": email,
                "password": "oddrun",
            })
        )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # save our cookies for later
        return response.cookies