"""`main` is the top level module for your application."""

import webapp2
import urllib2
from google.appengine.api import mail
from google.appengine.ext import db

import env

class SiteStatus(db.Model):
    up = db.BooleanProperty(required=True)

class Checker(webapp2.RequestHandler):
    def check(self):
        try:
            result = urllib2.urlopen(env.CHECK_URL, timeout=env.CHECK_TIMEOUT)
            return result.getcode() == 200
        except:
            return False

    def send_notice(self, up):
        if up == False:
            mail.send_mail(env.NOTIFY_FROM, env.NOTIFY_EMAIL, env.SUBJECT_DOWN, env.BODY_DOWN)
        else:
            mail.send_mail(env.NOTIFY_FROM, env.NOTIFY_EMAIL, env.SUBJECT_UP, env.BODY_UP)

    def get(self):
        db_key = db.Key.from_path('SiteStatus', 'previous_site_status')
        previous_site_status = db.get(db_key)

        status = True
        # Check twice to make sure the site is really down
        if self.check() == False and self.check() == False:
            status = False

        # Notify website being down or back up if there was a change in status
        if previous_site_status == None or previous_site_status.up != status:
            self.send_notice(status)

        site_status = SiteStatus(up=status, key_name='previous_site_status')
        site_status.put()

        self.response.headers['Content-Type'] = 'text/plain'
        if status == True:
            self.response.write("%s is UP" % env.CHECK_URL)
        else:
            self.response.write("%s is DOWN" % env.CHECK_URL)

app = webapp2.WSGIApplication([
    ('/check', Checker),
], debug=False)
