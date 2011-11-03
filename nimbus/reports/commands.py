#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.libs.commands import command
from nimbus.reports.models import send_email_report

@command("--email-report")
def email_report(job_id):
    send_email_report(job_id)



