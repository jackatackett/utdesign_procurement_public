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

def convertToDollarStr(cents):
    cents = int(cents)
    dollar = math.floor(cents / 100)
    cts = cents - (dollar * 100)
    return str(dollar) + "." + "{:02d}".format(cts)

class CostTester(TestCase):
    def test_cost(self):
        """
        Test the process of adding a cost.

        :return:
        """

        # get domain
        self.domain = 'http://localhost:8080'

        # connect to MongoDB
        client = pm.MongoClient()
        db = client['procurement']
        self.colCosts = db['costs']
        self.colProjects = db['projects']
        self.colUsers = db['users']

        # login as admin
        adminCookie = self.do_admin_login()

        # add costs to project 844
        for cost in ["refund", "reimbursement", "new budget"]:
            projectData = self.do_add_cost(adminCookie, cost, "5.00", 844)

        # login as manager/student to check if budget has been updated
        for user in ["student", "manager", "admin"]:
            self.do_login(user, projectData)

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

    def get_budget(self, cookies, projectNo):
        """
        Finds the budget for a project from the API and database.
        Tests /findProject endpoint

        :param cookies: CookieJar. Any authorized user
        :param projectNo: project number

        :return: (budget limit, available budget, pending budget)
        """

        #grab from API
        response = requests.post(
            "%s/findProject" % self.domain,
            cookies = cookies,
            headers = {
                'Content-type': 'application/json',
            },
            data = json.dumps({
                "projectNumbers": [projectNo]
            })
        )

        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        #grab from database
        dbData = self.colProjects.find_one({"projectNumber": projectNo})
        for key, val in json.loads(response.content.decode("utf-8"))[0].items():
            self.assertIn(key, dbData)
            if key == "_id":
                self.assertEqual(ObjectId(val), dbData[key])
            else:
                self.assertEqual(val, dbData[key])

        return dbData

    def do_add_cost(self, cookies, costType, amt, projectNo):
        """
        Add a cost to the specified project.
        This requires being logged in as an admin.

        :param cookies: CookieJar. A valid admin session id.
        :param costType: must be "refund", "reimbursement", or "new budget"
        :param amt: the cost to add in dollar format
        :param projectNo: project number

        :return: new project data
        """

        #grab current budget from api and db
        oldProjectData = self.get_budget(cookies, projectNo)
        #print(oldProjectData)

        response = requests.post(
            '%s/addCost' % self.domain,
            cookies = cookies,
            headers = {
                'Content-type': 'application/json',
            },
            data = json.dumps({
                "projectNumber": projectNo,
                "type": costType,
                "amount": amt,
                "comment": "unit test",
                "actor": "admin@utdallas.edu"
            })
        )

        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        #check if in database
        postCondition = {
            "projectNumber": projectNo,
            "type": costType,
            "amount": lenientConvertToCents(amt),
            "comment": "unit test",
            "actor": "admin@utdallas.edu"
        }

        costDoc = self.colCosts.find_one(postCondition)
        for key, val in postCondition.items():
            self.assertIn(key, costDoc)
            self.assertEqual(val, costDoc[key])

        #check if new project budget is accurate after inserting the cost
        newProjectData = self.get_budget(cookies, projectNo)

        if costType == "new budget":
            self.assertEqual(convertToDollarStr(newProjectData["defaultBudget"]), amt)
            self.assertEqual(newProjectData["pendingBudget"] - oldProjectData["pendingBudget"], newProjectData["availableBudget"] - oldProjectData["availableBudget"])
        else:
            self.assertEqual(oldProjectData["defaultBudget"], newProjectData["defaultBudget"])
            for budgetType in ["pendingBudget", "availableBudget"]:
                self.assertEqual(convertToDollarStr(abs(oldProjectData[budgetType] - newProjectData[budgetType])), amt)

        return newProjectData

    def do_login(self, user, projectData):
        """
        Login as the specified user and compares the view with the admin data.
        Tests the /findProject endpoint.

        :param user: "student", "manager", or "admin"
        :param projectData: data of the project to compare with
        """

        if user == "student":
            email = "marcus@utdallas.edu"
        elif user == "manager":
            email = "manager@utdallas.edu"
        elif user == "admin":
            email = "admin@utdallas.edu"
        else:
            self.assertEqual(True, False)
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

        # grab the project data from the endpoint
        response = requests.post(
            "%s/findProject" % self.domain,
            cookies = response.cookies,
            headers = {
                'Content-type': 'application/json',
            },
            data = json.dumps({
                "projectNumbers": [projectData["projectNumber"]]
            })
        )

        if not (200 <= response.status_code <= 300):
            raise ValueError(response.content.decode("utf-8"))

        # compare
        for key, val in json.loads(response.content.decode("utf-8"))[0].items():
            self.assertIn(key, projectData)
            if key == "_id":
                self.assertEqual(ObjectId(val), projectData[key])
            else:
                self.assertEqual(val, projectData[key])
