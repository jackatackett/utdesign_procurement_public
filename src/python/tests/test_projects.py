#!/usr/bin/env python3

import pymongo as pm
from bson.objectid import ObjectId
import json
import requests
import math

from unittest import TestCase

class ProjectTester(TestCase):
    def test_project:
        """
        Test the process of adding a project
        """

        # get domain
        self.domain = 'http://localhost:8080'

        # connect to MongoDB
        client = pm.MongoClient()
        db = client['procurement']
        self.colProjects = db['projects']
        self.colUsers = db['users']

        # login as admin
        adminCookie = self.do_admin_login()

        # add a project to an existing user

        # login as the user and check projects

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

    def add_project(self, cookies, student, manager, projectNumber, budget=None):
        """
        Adds a project. Must be performed by an admin.
        Tests the /addProject endpoint

        :param cookies: CookieJar. Any authorized user
        :param student: email of the student to be added; should be an existing user
        :param manager: email of the manager to be added; should be an existing user
        :param projectNumber: project number of new project
        :param budget: optional; dollar string of the budget

        :return: new project data
        """

        data = {
            "projectNumber": projectNumber,
            "sponsorName": "sponsor",
            "projectName": "test project",
            "membersEmails": [student, manager]
        }

        if budget is not None:
            data["defaultBudget"] = budget

        response = requests.post(
            '%s/userLogin' % self.domain,
            cookies = cookies,
            headers = {
                'Content-type': 'application/json'
            },
            data = json.dumps(data)
        )

        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # look in database for the project and compare
        postCondition = {
            "projectNumber": projectNumber,
            "sponsorName": "sponsor",
            "projectName": "test project",
            "membersEmails": [student, manager]
        }

        if budget is not None:
            postCondition["defaultBudget"] = budget #convert

        costDoc = self.colCosts.find_one(postCondition)
        for key, val in postCondition.items():
            self.assertIn(key, costDoc)
            self.assertEqual(val, costDoc[key])
