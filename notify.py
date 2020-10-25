#!/bin/bash

import smtplib
from os import environ


class Notify:
    """
    Send a notification to a recipient.
    """
    def __init__(self):
        # sender's email and password
        self.EMAIL_USER = environ.get("EMAIL_USER")
        self.EMAIL_PASSWORD = environ.get("EMAIL_PASSWORD")
        if self.EMAIL_USER is None or self.EMAIL_PASSWORD is None:
            print("Email user and password env variables are not set. Returning...")
            return

    @staticmethod
    def _build_email(subject: str, body: str) -> str:
        """
        Return the format needed for the email to be send using the smtp library.
        :param subject: subject of the email
        :type subject: str
        :param body: body of the email
        :type body: str
        :return: string in the format needed for the email to be send
        :rtype: str
        """
        return f"Subject: {subject}\n\n{body}"

    def send_email(self, recipient: str, email_subject: str, email_body: str):
        """
        Login to a SMTP server, build up the email and send the email.
        :param recipient: recipient of the email
        :type recipient: str
        :param email_subject: subject of the email
        :type email_subject: str
        :param email_body: body of the email
        :type email_body: str
        """
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as client:
            # login to smtp server
            client.login(self.EMAIL_USER, self.EMAIL_PASSWORD)

            # build email
            email = self._build_email(email_subject, email_body)

            # send email
            client.sendmail(from_addr=self.EMAIL_USER, to_addrs=recipient, msg=email)
