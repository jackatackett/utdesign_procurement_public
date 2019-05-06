#!/usr/bin/env python3

import smtplib
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.lookup import TemplateLookup
from multiprocessing import Process, Queue
from string import capwords

from utdesign_procurement.utils import convertToDollarStr

def email_listen(emailer, queue):
    """
    Listens for any messages that come through the queue and calls the
    emailer's send function appropriately

    :param emailer:
    :param queue:
    :return:
    """

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
    Fills templates and sends emails using an Emailer in a separate thread.

    In the various function names "confirm" refers to confirming that an
    action taken by a user has in fact been completed successfully.
    On the other hand "notify" is to notify the user that a different
    user has taken some action relevant to them.

    :param email_user: (str). Gmail username of the email account to be used
    :param email_password: (str). Password for the gmail account to be used
    :param email_inwardly: (bool). If True, emails are sent to the email_user
        and not to their intended recipient. Good for debugging.
    :param template_dir: (str). The directory for the mako templates.
    :param domain: (str). The domain name of the system. This will be used
        to populate URLs in templates.
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
        """
        Start the email queue listening process

        :return:
        """
        self.process.start()
        self._started = True

    def die(self):
        """
        End the email queue listening process gracefully

        :return:
        """

        if self._started:
            self.queue.put(('die', {}))
            self.process.join()

    def send(self, to, subject, body):
        """
        Send an email to an address, with a subject, with a given body.

        :param to: (str). The recipient email address.
        :param subject: (str). The subject of the email.
        :param body: (str). The HTML content of the message to send.
        :return:
        """

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
        Alerts team members that a procurement request has been submitted.

        :param: teamEmails: (list of str). The email addresses of the users
        :param: request: (dict). The request being notified about.
        :return:
        """

        # TODO cast to int
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

        subject = 'New Request For Project %s' % int(request['projectNumber'])

        # send email to students
        template = self.templateLookup.get_template('procurementSaveStudent.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

        # send email to manager
        template = self.templateLookup.get_template('procurementSaveManager.html')
        body = template.render(**renderArgs)
        self.send(request['manager'], subject, body)

    def procurementEditAdmin(self, teamEmails=None, request=None):
        """
        Alerts team members that a procurement request has been submitted.

        :param: teamEmails: (list of str). The email addresses of the users
        :param: request: (dict). The request being notified about.
        :return:
        """

        renderArgs = {

            # TODO cast to int
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

        subject = 'Request #%s Updated For Project %s' % (int(request['requestNumber']), int(request['projectNumber']))
        template = self.templateLookup.get_template('procurementUpdated.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)
        self.send(request['manager'], subject, body)

    def confirmStudent(self, teamEmails, requestNumber, projectNumber, action):
        """
        Sends an email to all members of a team confirming that some
        action has happened to some request.

        :param: teamEmails: (list of str). The email addresses of the users
        :param: requestNumber: (dict). The request being notified about.
        :param: projectNumber: (dict). The project whose members are being notified.
        :param: action: (dict). The action happening to the request.
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber),
            'action': action
        }
        capitalAction = capwords(action)
        subject = 'Request #%s Has Been %s' % (int(requestNumber), capitalAction)
        template = self.templateLookup.get_template('confirmStudent.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

    def confirmRequestManagerAdmin(self, email, requestNumber, projectNumber, action):
        """
        Sends an email to some email address confirming that some
        action has happened to some request.

        :param email:
        :param requestNumber:
        :param projectNumber:
        :param action:
        :return:
        """
        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber),
            'action': action
        }
        capitalAction = capwords(action)
        subject = 'Request #%s Has Been %s' % (int(requestNumber), capitalAction)
        template = self.templateLookup.get_template('confirmRequestManagerAdmin.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyStudent(self, teamEmails, requestNumber, projectNumber, action,
                      user, role):
        """
        Sends a notification about a request to some students.

        :param teamEmails:
        :param requestNumber:
        :param projectNumber:
        :param action:
        :param user:
        :param role:
        :return:
        """
        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber),
            'action': action,
            'user': user,
            'role': role
        }
        capitalAction = capwords(action)
        subject = 'Request #%s Has Been %s' % (int(requestNumber), capitalAction)
        template = self.templateLookup.get_template('notifyStudent.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

    def notifyRequestManager(self, email, projectNumber, requestNumber):
        """
        Sends a notification about a request to a manager.

        :param email:
        :param projectNumber:
        :param requestNumber:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber)
        }
        subject = "Request #%s Has Been Submitted to You" % (int(requestNumber))
        template = self.templateLookup.get_template('notifyRequestManager.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyRequestAdmin(self, adminEmails, projectNumber, requestNumber):
        """
        Sends a notification about a request to the admins.

        :param adminEmails:
        :param projectNumber:
        :param requestNumber:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber)
        }
        subject = "Request #%s Needs Admin Approval" % (int(requestNumber))
        template = self.templateLookup.get_template('notifyRequestAdmin.html')
        body = template.render(**renderArgs)
        self.send(adminEmails, subject, body)

    def notifyCancelled(self, email, projectNumber, requestNumber):
        """
        Notify some user about the cancellation of a request.

        :param email:
        :param projectNumber:
        :param requestNumber:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber)
        }
        subject = "Request #%s Has Been Cancelled" % (int(requestNumber))
        template = self.templateLookup.get_template('notifyCancelled.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyRejectedAdmin(self, adminEmails, projectNumber, requestNumber, manager):
        """
        Notify some users that the admin has rejected a request.

        :param adminEmails:
        :param projectNumber:
        :param requestNumber:
        :param manager:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber),
            'manager': manager
        }
        subject = "Request #%s Has Been Rejected" % (int(requestNumber))
        template = self.templateLookup.get_template('notifyRejectedAdmin.html')
        body = template.render(**renderArgs)
        self.send(adminEmails, subject, body)

    def notifyUserEdit(self, email, projectNumbers, firstName, lastName, netID, course):
        """
        Notify some users that a user has edited a request.

        :param email:
        :param projectNumbers:
        :param firstName:
        :param lastName:
        :param netID:
        :param course:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'projectNumbers': projectNumbers,
            'firstName': firstName,
            'lastName': lastName,
            'netID': netID,
            'course': course
        }
        subject = "You Have Been Edited!"
        template = self.templateLookup.get_template('notifyUserEdit.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyUpdateManager(self, email, projectNumber, requestNumber):
        """
        Notify some user that the manager has requested updates.

        :param email:
        :param projectNumber:
        :param requestNumber:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'projectNumber': int(projectNumber),
            'requestNumber': int(requestNumber)
        }
        subject = "Request #%d Has Been Sent For Updates!" % (requestNumber)
        template = self.templateLookup.get_template('notifyUpdateManager.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyUserRemove(self, email, firstName, lastName):
        """
        Notify a user that their account has been deactivated.

        :param email:
        :param firstName:
        :param lastName:
        :return:
        """

        renderArgs = {
            'email': email,
            'firstName': firstName,
            'lastName': lastName
        }
        subject = "Your GettIt Account Has Been Deactivated"
        template = self.templateLookup.get_template('notifyUserRemove.html')
        body = template.render(**renderArgs)
        self.send(email, subject, body)

    def notifyProjectAdd(self, teamEmails, projectNumber, projectName):
        """
        Notify a user that they have been added to a project.

        :param teamEmails:
        :param projectNumber:
        :param projectName:
        :return:
        """
        renderArgs = {
            'domain': self.domain,
            'projectNumber': int(projectNumber),
            'projectName': str(projectName),
        }
        subject = "You Have Been Added to Project %s" % (int(projectNumber))
        template = self.templateLookup.get_template('notifyProjectAdd.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

    def notifyProjectInactivate(self, teamEmails, projectNumber, projectName):
        """
        Notify a user that a project that they were a member of has been deactivated.

        :param teamEmails:
        :param projectNumber:
        :param projectName:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'projectNumber': int(projectNumber),
            'projectName': projectName,
        }
        subject = "Project Number %s Has Been Inactivated" % (int(projectNumber))
        template = self.templateLookup.get_template('notifyProjectInactivate.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

    def notifyProjectEdit(self, membersEmails, projectNumber, projectName, sponsorName):
        """
        Notify a user that a project that they were a member of has been edit.

        :param teamEmails:
        :param projectNumber:
        :param projectName:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'projectNumber': int(projectNumber),
            'projectName': str(projectName),
            'membersEmails': membersEmails,
            'sponsorName': sponsorName
        }
        subject = "Project Number %s Has Been Edited" % (int(projectNumber))
        template = self.templateLookup.get_template('notifyProjectEdit.html')
        body = template.render(**renderArgs)
        self.send(membersEmails, subject, body)

    def notifyStudentRejected(self, teamEmails, requestNumber, projectNumber, action,
                      user, role, comment):
        """
        Notify a user that a request has been rejected.

        :param teamEmails:
        :param projectNumber:
        :param projectName:
        :return:
        """

        renderArgs = {
            'domain': self.domain,
            'requestNumber': int(requestNumber),
            'projectNumber': int(projectNumber),
            'action': action,
            'user': user,
            'role': role,
            'comment': comment
        }
        capitalAction = capwords(action)
        print(capitalAction)
        subject = 'Request #%s Has Been %s' % (int(requestNumber), capitalAction)
        template = self.templateLookup.get_template('notifyStudentRejected.html')
        body = template.render(**renderArgs)
        self.send(teamEmails, subject, body)

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
        """
        Send an email with some HTML content to some email address with some
        subject.

        :param to: (str). An email address to send to.
        :param subject: (str). A subject for the email.
        :param html: (str). An HTML content to send in the email.
        :return:
        """

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
