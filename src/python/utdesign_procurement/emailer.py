#!/usr/bin/env python3

import smtplib
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.lookup import TemplateLookup
from multiprocessing import Process, Queue

from utdesign_procurement.utils import convertToDollarStr

def email_listen(emailer, queue):
    function_lut = {
        'send': emailer.emailSend,
    }

    while True:
        packet = queue.get()

        try:
            header, kwargs = packet
        except:
            continue

        func = function_lut.get(header, None)
        if func:
            try:
                func(**kwargs)
            except Exception as e:
                print("Emailer encountered an exception.")
                traceback.print_exc()
        elif header == 'die':
            break

class EmailHandler(object):
    """
    Fills templates and sends emails using an Emailer in a separate thread
    """

    def __init__(self, email_user, email_password, email_inwardly,
                 template_dir, domain='utdprocure.utdallas.edu'):

        self.domain = domain
        self.templateLookup = TemplateLookup(template_dir)

        self.queue = Queue()
        self.emailer = Emailer(self.queue, email_user, email_password, email_inwardly)
        self.process = Process(target=email_listen, args=(self.emailer, self.queue))
        self._started = False

    def start(self):
        self.process.start()
        self._started = True

    def die(self):
        if self._started:
            self.queue.put(('die', {}))
            self.process.join()

    def send(self, to, subject, body):
        self.queue.put(('send', {
            'to': to,
            'subject': subject,
            'html': body
        }))

    def userAdd(self, email=None, uuid=None):
        """
        Sends an invitation for a new user to set up their password for the
        first time.

        :param email: The email of the user
        :param uuid: The uuid used for the invitation
        :return:
        """

        template = self.templateLookup.get_template('userAdd.html')
        body = template.render(uuid=uuid, domain=self.domain)
        self.send(email, 'UTDesign GettIt Invite', body)

    def userForgotPassword(self, email=None, uuid=None, expiration=None):
        """
        Sends a recovery link for an existing user to reset their password.

        :param email:
        :param uuid:
        :param expiration:
        :return:
        """

        template = self.templateLookup.get_template('userForgotPassword.html')
        body = template.render(uuid=uuid, domain=self.domain, expiration=expiration)
        self.send(email, 'UTDesign GettIt Password Reset', body)

    def procurementSave(self, teamEmails=None, request=None):
        """

        :param request:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': request['requestNumber'],
            'projectNumber': request['projectNumber'],
            'managerEmail': request['manager'],
            'vendor': request['vendor'],
            'vendorURL': request['URL'],
            'justification': request['justification'],
            'additionalInfo': request['additionalInfo'],
            'itemCount': len(request['items'])
        }

        subject = 'New Request For Project %s' % request['projectNumber']
        template = self.templateLookup.get_template('procurementSaveStudent.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)
        self.send(request['manager'], subject, body)

    def procurementEditAdmin(self, teamEmails=None, request=None):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': request['requestNumber'],
            'projectNumber': request['projectNumber'],
            'managerEmail': request['manager'],
            'vendor': request['vendor'],
            'vendorURL': request['URL'],
            'justification': request['justification'],
            'additionalInfo': request['additionalInfo'],
            'itemCount': len(request['items']),
            'shippingCost': convertToDollarStr(request['shippingCost'])
        }

        subject = 'Request Updated For Project %s' % request['projectNumber']
        template = self.templateLookup.get_template('procurementUpdated.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)
        self.send(request['manager'], subject, body)

    def confirmStudent(self, teamEmails, requestNumber, projectNumber, action):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber,
            'action': action
        }

        subject = 'Request %s is now %s' % (requestNumber, action)
        template = self.templateLookup.get_template('confirmStudent.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

    def confirmRequestManagerAdmin(self, email, requestNumber, projectNumber, action):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber,
            'action': action
        }

        subject = 'Request %s is now %s' % (requestNumber, action)
        template = self.templateLookup.get_template('confirmRequestManagerAdmin.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyStudent(self, teamEmails, requestNumber, projectNumber, action,
                      user, role):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber,
            'action': action,
            'user': user,
            'role': role
        }

        subject = 'Request %s has been %s' % (requestNumber, action)
        template = self.templateLookup.get_template('notifyStudent.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

    def notifyRequestManager(self, email, projectNumber, requestNumber):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber
        }
        subject = "Request %s has been submitted to you" % (requestNumber)
        template = self.templateLookup.get_template('notifyRequestManager.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyRequestAdmin(self, adminEmails, projectNumber, requestNumber):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber
        }
        subject = "Request %s needs admin approval" % (requestNumber)
        template = self.templateLookup.get_template('notifyRequestAdmin.html')
        body = template.render(**renderArgs)
        self.send(adminEmails, subject, body)

    def notifyCancelled(self, email, projectNumber, requestNumber):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber
        }
        subject = "Request %s has been cancelled" % (requestNumber)
        template = self.templateLookup.get_template('notifyCancelled.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyRejectedAdmin(self, adminEmails, projectNumber, requestNumber, manager):
        renderArgs = {
            'domain': self.domain,
            'requestNumber': requestNumber,
            'projectNumber': projectNumber,
            'manager': manager
        }
        subject = "Request %s has been rejected" % (requestNumber)
        template = self.templateLookup.get_template('notifyRejectedAdmin.html')
        body = template.render(**renderArgs)
        self.send(adminEmails, subject, body)

    def notifyUserEdit(self, email, projectNumbers, firstName, lastName, netID, course):
        renderArgs = {
            'domain': self.domain,
            'projectNumbers': projectNumbers,
            'firstName': firstName,
            'lastName': lastName,
            'netID': netID,
            'course': course
        }
        subject = "You have been edited!"
        template = self.templateLookup.get_template('notifyUserEdit.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyUpdateManager(self, email, projectNumber, requestNumber):
        renderArgs = {
            'domain': self.domain,
            'projectNumber': projectNumber,
            'requestNumber': requestNumber
        }
        subject = "Request % has been sent for updates!" % (requestNumber)
        template = self.templateLookup.get_template('notifyUpdateManager.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyUserRemove(self, email, firstName, lastName):
        renderArgs = {
            'email': email,
            'firstName': firstName,
            'lastName': lastName
        }
        subject = "Your GettIt account has been deactivated"
        template = self.templateLookup.get_template('notifyUserRemove.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

class Emailer(object):
    """
    Manages email connections and sends HTML emails in MIMEMultipart messages
    """

    def __init__(self, email_queue, email_user, email_password, email_inwardly):
        self.email_queue = email_queue
        self.email_user = email_user
        self.email_password = email_password
        self.email_inwardly = email_inwardly

    def _emailDo(self, func):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.email_user, self.email_password)
        func(server)
        server.quit()

    def emailSend(self, to=None, subject=None, html=None):
        assert to and subject

        if self.email_inwardly:
            subject = '[DEBUG %s] %s' % (to, subject)
            to = self.email_user

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_user
        if isinstance(to, str):
            msg['To'] = to
        else:
            msg['To'] = ','.join(to)

        msg.attach(MIMEText("This email is meant to be HTML.", 'plain'))
        msg.attach(MIMEText(html, 'html'))

        self._emailDo(
            lambda server: server.sendmail(self.email_user, to, msg.as_string()))
