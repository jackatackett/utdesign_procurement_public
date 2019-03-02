#!/usr/bin/env python3

import smtplib

from multiprocessing import Process, Queue

def email_listen(emailer, queue):
    function_lut = {
        'invite': emailer.emailInvite,
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


def fork_emailer(email_user, email_password, email_inwardly):
    queue = Queue()
    emailer = Emailer(queue, email_user, email_password, email_inwardly)
    process = Process(target=email_listen, args=(emailer, queue))
    return process, queue

class Emailer(object):

    def __init__(self, email_queue, email_user, email_password, email_inwardly):
        self.email_queue = email_queue
        self.email_user = email_user
        self.email_password = email_password
        self.email_inwardly = email_inwardly

    def emailInvite(self, email=None, uuid=None, expiration=None):
        # TODO make this message pretty
        # TODO include expiration time in this email
        body = ('You have been invited to use the UTDesign GettIt system!\n'
                'Hooray!\n'
                '\n'
                '\n'
                'Go to this link to set up your account:\n'
                'http://localhost:8080/verify?id=%s\n')

        body %= uuid

        self._emailSend(email, 'UTDesign GettIt Invite', body)

    def _emailDo(self, func):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.email_user, self.email_password)
        func(server)
        server.quit()

    def _emailSend(self, to, subject, body):
        if self.email_inwardly:
            subject = '[DEBUG %s] %s' % (to, subject)
            to = self.email_user

        email_text = '\n'.join((
            'From: %s' % self.email_user,
            'To: %s' % (to if isinstance(to, str) else ', '.join(to)),
            'Subject: %s' % subject,
            '',
            body))

        self._emailDo(
            lambda server: server.sendmail(self.email_user, to, email_text))
