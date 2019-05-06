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

        requestId, requestNumber = self.do_save_request(
            student_cookies,
            manager_email,
            project_number)

        self.assertNotEqual(-1, requestNumber)

        self.do_create_request(
            requestNumber,
            student_cookies,
            manager_email,
            project_number)

        self.do_update_manager(
            requestId,
            manager_cookies,
        )

        self.do_resubmit_to_manager(
            requestId,
            student_cookies,
            project_number,
        )

        self.do_approve_manager(
            requestId,
            manager_cookies,
        )

        self.do_update_manager_admin(
            requestId,
            admin_cookies,
        )

        self.do_resubmit_to_manager(
            requestId,
            student_cookies,
            project_number,
        )

        self.do_approve_manager(
            requestId,
            manager_cookies,
        )

        self.do_update_admin(
            requestId,
            admin_cookies,
        )

        self.do_resubmit_to_admin(
            requestId,
            student_cookies,
            project_number
        )

        self.do_order(
            requestId,
            admin_cookies,
        )

        self.do_ready(
            requestId,
            admin_cookies,
        )

        self.do_complete(
            requestId,
            admin_cookies,
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

    def do_save_request(self, student_cookies, manager_email, project_number):
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

        return requestId, userDoc.get('requestNumber', -1)

    def do_create_request(self, requestNumber, student_cookies, manager_email, project_number):
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
                "requestNumber": requestNumber,
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

    def do_update_manager(self, requestId, cookies):
        """
        Test the /procurementUpdateManager REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
            "comment":""
        }

        response = requests.post(
            '%s/procurementUpdateManager' % self.domain,
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
        self.assertEqual('updates for manager', requestDoc['status'])

    def do_resubmit_to_manager(self, requestId, cookies, project_number):
        """
        Test the /procurementResubmitToManager REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id": requestId,
            "items": [{
                "partNo":"1",
                "unitCost":"4.19",
                "description":"Prophecy",
                "itemURL":"https://www.oracle.com/prophecy",
                "totalCost":"4.19",
                "quantity":1
            }],
            "projectNumber": project_number,
            "URL":"844",
            "vendor":"Oracle",
            "additionalInfo":"There are big winnings to be had",
            "requestNumber":7,
            "manager":"manager@utdallas.edu",
            "justification":"I want to win the lottery",
            "submit": True
        }

        response = requests.post(
            '%s/procurementResubmitToManager' % self.domain,
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
        self.assertEqual('pending', requestDoc['status'])

    def do_approve_manager(self, requestId, cookies):
        """
        Test the /procurementApproveManager REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
        }

        response = requests.post(
            '%s/procurementApproveManager' % self.domain,
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
        self.assertEqual('manager approved', requestDoc['status'])

    def do_update_manager_admin(self, requestId, cookies):
        """
        Test the /procurementUpdateManagerAdmin REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
            "comment": ""
        }

        response = requests.post(
            '%s/procurementUpdateManagerAdmin' % self.domain,
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
        self.assertEqual('updates for manager', requestDoc['status'])

    def do_update_admin(self, requestId, cookies):
        """
        Test the /procurementUpdateAdmin REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
            "comment": ""
        }

        response = requests.post(
            '%s/procurementUpdateAdmin' % self.domain,
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
        self.assertEqual('updates for admin', requestDoc['status'])

    def do_resubmit_to_admin(self, requestId, cookies, project_number):
        """
        Test the /procurementResubmitToAdmin REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id": requestId,
            "items": [{
                "partNo":"1",
                "unitCost":"4.19",
                "description":"Prophecy",
                "itemURL":"https://www.oracle.com/prophecy",
                "totalCost":"8.38",
                "quantity":2
            }],
            "projectNumber": project_number,
            "URL":"844",
            "vendor":"Oracle",
            "additionalInfo":"There are big winnings to be had",
            "requestNumber":7,
            "manager":"manager@utdallas.edu",
            "justification":"I want to win the lottery",
            "submit": True
        }

        response = requests.post(
            '%s/procurementResubmitToAdmin' % self.domain,
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
        self.assertEqual('manager approved', requestDoc['status'])

    def do_order(self, requestId, cookies):
        """
        Test the /procurementUpdateAdmin REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
            "amount":"2.00"
        }

        response = requests.post(
            '%s/procurementOrder' % self.domain,
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
        self.assertEqual('ordered', requestDoc['status'])

    def do_ready(self, requestId, cookies):
        """
        Test the /procurementReady REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
        }

        response = requests.post(
            '%s/procurementReady' % self.domain,
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
        self.assertEqual('ready for pickup', requestDoc['status'])

    def do_complete(self, requestId, cookies):
        """
        Test the /procurementReady REST endpoint.

        :param uuid: str. The uuid of the user invitation.
        :param email: str. The email address of the user to be added.

        :return:
        """

        data = {
            "_id":requestId,
        }

        response = requests.post(
            '%s/procurementComplete' % self.domain,
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
        self.assertEqual('complete', requestDoc['status'])


