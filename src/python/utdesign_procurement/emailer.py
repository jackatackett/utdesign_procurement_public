#!/usr/bin/env python3

import smtplib
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.lookup import TemplateLookup
from multiprocessing import Process, Queue

def email_listen(emailer, queue):
    function_lut = {
        'invite': emailer.emailInvite,
        'forgot': emailer.emailForgot,
        'send': emailer._emailSend,
        'requestMade': emailer.emailRequestMade
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


def fork_emailer(email_user, email_password, email_inwardly,
                 template_dir, domain='utdprocure.utdallas.edu'):
    queue = Queue()
    emailer = Emailer(queue, email_user, email_password, email_inwardly,
                      template_dir, domain)
    process = Process(target=email_listen, args=(emailer, queue))
    return process, queue

class Emailer(object):

    def __init__(self, email_queue, email_user, email_password, email_inwardly,
                 template_dir, domain):
        self.email_queue = email_queue
        self.email_user = email_user
        self.email_password = email_password
        self.email_inwardly = email_inwardly
        self.templateLookup = TemplateLookup(directories=template_dir)
        self.domain = domain

    def emailInvite(self, email=None, uuid=None):
        """
        Sends an invitation for a new user to set up their password for the
        first time.

        :param email: The email of the user
        :param uuid: The uuid used for the invitation
        :return:
        """

        template = self.templateLookup.get_template('userAdd.html')
        body = template.render(uuid=uuid, domain=self.domain)
        self._emailSend(email, 'UTDesign GettIt Invite', html=body)

    def emailForgot(self, email=None, uuid=None, expiration=None):
        """
        Sends a recovery link for an existing user to reset their password.

        :param email:
        :param uuid:
        :param expiration:
        :return:
        """

        template = self.templateLookup.get_template('userForgotPassword.html')
        body = template.render(uuid=uuid, domain=self.domain)
        self._emailSend(email, 'UTDesign GettIt Password Reset', html=body)

    def emailRequestMade(self, teamEmails=None, request=None):
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

        template = self.templateLookup.get_template('procurementSaveStudent.html')
        body = template.render(**renderArgs)
        self._emailSend(teamEmails, 'New Request For Project %s' % request['projectNumber'], html=body)

        template = self.templateLookup.get_template('procurementSaveManager.html')
        body = template.render(**renderArgs)
        self._emailSend(request['manager'], 'New Request For Project %s' % request['projectNumber'], html=body)

    def _emailDo(self, func):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.email_user, self.email_password)
        func(server)
        server.quit()

    def _emailSend(self, to=None, subject=None, html=None):
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
