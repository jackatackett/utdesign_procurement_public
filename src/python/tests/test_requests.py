#!/usr/bin/env python3

import pymongo as pm
import json
import requests

from unittest import TestCase
from bson.objectid import ObjectId

class RequestsTester(TestCase):
    """
    Tests the sequence of events for creating a procurement request.

    This class will log in as a student, a manager of that student's project,
    and the admin, then go through the whole approval and rejection process.

    """

    def test_requests(self):
        """
        Tests the sequence of events for creating a procurement request.

        :return:
        """

        # get domain
        self.domain = 'http://localhost:8080'

        # connect to MongoDB
        client = pm.MongoClient()
        db = client['procurement']
        self.colRequests = db['requests']

        # log in as each user
        # TODO, don't hardcode credentials here
        student_email = 'xander@utdallas.edu'
        manager_email = 'manager@utdallas.edu'
        admin_email = 'admin@utdallas.edu'

        student_password = manager_password = admin_password = 'oddrun'

        project_number = 844

        student_cookies = self.do_user_login(student_email, student_password)
        self.assertIn('session_id', student_cookies)
        manager_cookies = self.do_user_login(manager_email, manager_password)
        self.assertIn('session_id', manager_cookies)
        admin_cookies = self.do_user_login(admin_email, admin_password)
        self.assertIn('session_id', admin_cookies)

        requestId = self.do_create_request(
            student_cookies,
            manager_email,
            project_number)

        print(requestId)

        self.do_request_transition(
            endpoint='%s/procurementApproveManager' % self.domain,
            requestId=requestId,
            newStatus='manager approved',
            cookies=manager_cookies,
            data={'_id': requestId}
        )



    def do_user_login(self, email, password):
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
                "email": email,
                "password": password,
            })
        )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # save our cookies for later
        return response.cookies

    def do_create_request(self, student_cookies, manager_email, project_number):
        """
        Test the /procurementSave REST endpoint.
        This requires being logged in as a student.

        :param cookies: CookieJar. A valid student session id.

        :return: str. The MongoDB ObjectId of the request created
        """

        # send our user to be created
        response = requests.post(
            '%s/procurementSave' % self.domain,
            cookies = student_cookies,
            headers = {
                'Content-type': 'application/json'
            },
            data = json.dumps({
                "submit": True,
                "manager": manager_email,
                "vendor": 'Oracle',
                "projectNumber": project_number,
                "URL": 'https://www.oracle.com/index.html',
                "justification": 'I want to win the lottery',
                "additionalInfo": 'There are big winnings to be had',
                "items": [{
                    "description": "Prophecy",
                    "partNo": "1",
                    "itemURL": 'https://www.oracle.com/prophecy',
                    "quantity": 1,
                    "unitCost": "4.20",
                    "totalCost": "4.20"
                }]
            }),
        )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # save the uuid
        j = json.loads(response.content.decode('utf-8'))
        self.assertIn('_id', j)
        requestId = j['_id']

        # see if his user data is in MongoDB now
        postCondition = {
            "manager": manager_email,
            "vendor": 'Oracle',
            "projectNumber": project_number,
            "URL": 'https://www.oracle.com/index.html',
            "justification": 'I want to win the lottery',
            "additionalInfo": 'There are big winnings to be had',
        }

        userDoc = self.colRequests.find_one({"_id": ObjectId(requestId)})
        for key, val in postCondition.items():
            self.assertIn(key, userDoc)
            self.assertEqual(val, userDoc[key])

        return requestId

    def do_request_transition(self, endpoint, requestId, newStatus, cookies, data=None):
        """
        Test the /userVerify REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        # call the rest endpoint
        if data is None:
            response = requests.post(
                endpoint,
                cookies = cookies,
            )
        else:
            response = requests.post(
                endpoint,
                cookies = cookies,
                headers = {
                    'Content-type': 'application/json'
                },
                data = json.dumps(data),
            )

        # see if the response comes back okay
        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # check that the request with the given id now has the proper status
        requestDoc = self.colRequests.find_one({"_id": ObjectId(requestId)})
        self.assertTrue(requestDoc)
        self.assertIn('status', requestDoc)
        self.assertEqual(newStatus, requestDoc['status'])