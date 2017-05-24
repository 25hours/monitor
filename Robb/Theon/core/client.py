import time
from conf import settings
import urllib
import urllib2
import json
import threading
from plugins import plugin_api

class ClientHandle(object):
    def __init__(self):
        self.monitored_services = {}

    def load_latest_configs(self):
        '''
        load the latest monitor configs from monitor server
        :return:
        '''
        reuqest_type = settings.configs['urls']['get_configs'][1]
        url = "%s/%s" %(settings.configs['urls']['get_configs'][0],settings.configs['HostID'])
        latest_configs = self.url_request(reuqest_type,url)
        latest_configs = json.loads(latest_configs)
        self.monitored_services.update(latest_configs)
        print("------monitored_services------",self.monitored_services)

    def forever_run(self):
        '''
        start the client program forever
        :return:
        '''
        exit_flag = False
        config_last_update_time = 0
        while not exit_flag:
            if time.time() - config_last_update_time > settings.configs['ConfigUpdateInterval']:
                self.load_latest_configs()
                print("Loaded latest config:",self.monitored_services)
                config_last_update_time = time.time()
                #start to monitor services

            for service_name,val in self.monitored_services['services'].items():
                if len(val) == 2:   #first time to monitor
                    self.monitored_services['services'][service_name].append(0)
                monitor_interval = val[1]
                last_invoke_time = val[2]
                if time.time() - last_invoke_time > monitor_interval:
                    print(last_invoke_time,time.time())
                    self.monitored_services['services'][service_name][2] = time.time()
                    t = threading.Thread(target=self.invoke_plugin,args=(service_name,val))
                    t.start()
                    print("going ti monitor [%s]" % service_name)
                else:
                    print("going to monitor [%s] in [%s] secs" % (service_name,))

    def invoke_plugin(self,service_name,val):
        '''
        invoke the monitor plugin here,and send the data to monitor
        :param service_name:
        :param val:
        :return:
        '''
        plugin_name = val[0]
        if hasattr(plugin_api,plugin_name):
            func = getattr(plugin_api,plugin_name)
            plugin_callback = func()

            report_data = {
                'client_id':settings.configs['HostID'],
                'service_name':service_name,
                'data':json.dumps(plugin_callback)
            }

            request_action = settings.configs['urls']['service_report'][1]
            request_url = settings.configs['urls']['service_report'][0]

            print("---report data:",report_data)
            self.url_request(request_action,request_url,params=report_data)
        else:
            print("\033[31;1mCannot find plugin name [%s] in plugin_api\033[0m" % plugin_name)
        print("---plugin:",val)

    def utl_request(self,action,url,**extra_data):
        '''
        copy with monitor server by url
        :param action:
        :param url:
        :param extra_data:
        :return:
        '''
        abs_url = "http://%s:%s/%s" % (settings.configs['Server'],
                                       settings.configs[""],
                                       url
                                       )
        if action in ('get','GET'):
            print(abs_url,extra_data)
            try:
                req = urllib2.Request(abs_url)
                req_data = urllib2.urlopen(req,timeout=settings.configs['RequestTimeout'])
                callback = req_data.read()
                return callback
            except urllib2.URLError as e:
                exit("\033[31;1m%s\033[0m" % e)

        elif action in ('post','POST'):
            try:
                data_encode = urllib.urlencode(extra_data['params'])
                req = urllib2.Request(url=abs_url,data=data_encode)
                res_data = urllib2.urlopen(req,timeout=settings.configs)
                callback = res_data.read()
                callback = json.loads(callback)
                print("\033[31;1m[%s]:[%s]\033[0m response:\n%s" %(action,abs_url,callback))
                return callback
            except Exception as e:
                print("---exec",e)
                exit("\033[31;1m%s\033[0m" % e)