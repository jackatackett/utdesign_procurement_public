#!/usr/bin/env python3

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.lookup import TemplateLookup
from multiprocessing import Process, Queue

def email_listen(emailer, queue):
    function_lut = {
        'invite': emailer.emailInvite,
        'forgot': emailer.emailForgot,
        'send': emailer._emailSend
    }

    while True:
        packet = queue.get()

        try:
            header, kwargs = packet
        except:
            continue

        func = function_lut.get(header, None)
        if func:
            func(**kwargs)
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

        template = self.templateLookup.get_template('invite.html')
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

        template = self.templateLookup.get_template('forgot.html')
        body = template.render(uuid=uuid, domain=self.domain)
        self._emailSend(email, 'UTDesign GettIt Password Reset', html=body)

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
        msg['To'] = to

        msg.attach(MIMEText("This email is meant to be HTML.", 'plain'))
        msg.attach(MIMEText(html, 'html'))

        self._emailDo(
            lambda server: server.sendmail(self.email_user, to, msg.as_string()))
