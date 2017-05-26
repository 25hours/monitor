import os,sys
import django
django.setup()
from Robb.backends import data_processing,trigger_handler
from monitor import settings

class ManagementUtility(object):
    def __init__(self,argv=None):
        self.agrv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.agrv[0])
        self.settings_execption = None
        self.registered_actions = {
            'start':self.start,
            'stop':self.stop,
            'trigger_watch':self.trigger_watch,
        }
        self.agrv_check()

    def argv_check(self):


    def trigger_watch(self):
        trigger_watch = trigger_handler.TriggerHandler(settings)
        trigger_watch.start_watching()