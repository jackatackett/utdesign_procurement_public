#!/usr/bin/env python3

import pymongo as pm
from bson.objectid import ObjectId
import json
import requests
import math

from unittest import TestCase

import sys
sys.path.insert(0, '../utdesign_procurement')
from utils import lenientConvertToCents

class ProjectTester(TestCase):
    def test_project(self):
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
        self.add_project(adminCookie, "student1@utdallas.edu", "manager@utdallas.edu", 1, "2500.50")

        # login as the users and check projects
        self.verify_projects(["student1@utdallas.edu", "manager@utdallas.edu"], 1)

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

    def add_project(self, cookies, student, manager, projectNumber, budget="2000.00"):
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
            "membersEmails": [student, manager],
            "defaultBudget": budget,
            "availableBudget": budget,
            "pendingBudget": budget
        }

        response = requests.post(
            '%s/projectAdd' % self.domain,
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
            "membersEmails": [student, manager],
            "defaultBudget": lenientConvertToCents(budget),
            "availableBudget": lenientConvertToCents(budget),
            "pendingBudget": lenientConvertToCents(budget)
        }

        costDoc = self.colProjects.find_one(postCondition)
        for key, val in postCondition.items():
            self.assertIn(key, costDoc)
            self.assertEqual(val, costDoc[key])

        return postCondition

    def verify_projects(self, userList, projectNumber):
        """
        Logins as each user in the userList, and verifies that projectNumber is in their projects

        :param userList: array of user emails
        :param projectNumber: projectNumber to test for
        """
        for user in userList:
            response = requests.post(
                '%s/userLogin' % self.domain,
                headers = {
                    'Content-type': 'application/json'
                },
                data = json.dumps({
                    "email": user,
                    "password": "oddrun",
                })
            )

            # see if the response comes back okay
            if not (200 <= response.status_code <= 300):
                raise ValueError(response.content.decode("utf-8"))

            # save our cookies for later
            authCookie = response.cookies

            # look up with request to API the projects assigned to the user
            response = requests.post(
                '%s/findProject' % self.domain,
                cookies = authCookie,
                headers = {
                    'Content-type': 'application/json'
                },
                data = json.dumps({})
            )

            if not (200 <= response.status_code <= 300):
                raise ValueError(response.content.decode("utf-8"))

            self.assertIn(projectNumber, [apiResp["projectNumber"] for apiResp in json.loads(response.content.decode("utf-8"))])

            # look up in database to verify
            self.assertIn(projectNumber, list(self.colUsers.find({"email": user}))[0]["projectNumbers"])
