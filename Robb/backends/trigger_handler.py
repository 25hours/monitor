from Robb.backends import redis_conn
import pickle,time
from Robb import models

class TriggerHandler(object):
    def __init__(self,django_setting):
        self.django_settings = django_setting
        self.redis = redis_conn.redis_conn(self.django_settings)
        self.alert_counter = {}
        alert_counters = {
            1:{
                2:{'counter':0,'last_alert':None},
                4:{'counter':1,'last_alert':None},
            },
        }

    def start_watching(self):
        radio = self.redis.publish()
        radio.subscribe(self.django_settings.TRIGGER_CHAN)
        radio.parse_response()
        print("\033[43;1m-----------start listening new triggers--------\033[0m")
        self.trigger_count = 0
        while True:
            msg = radio.parse_response()
            self.trigger_consume(msg)


    def trigger_consume(self,mag):
        self.trigger_count += 1
        print("\033[41;1m-----------Got a trigger msg [%s]------\033[0m" % self.)
        trigger_msg = pickle.loads(msg[2])
        action = ActionHandler(trigger_msg,self.alert_counters)
        action.triggers_process()

class ActionHandler(object):
    def __init__(self,trgger_data,alert_counter_dic):
        self.trigger_data = trgger_data
        self.alert_counter_dic = alert_counter_dic

    def trigger_process(self):
        print("Action Processing".center(50,'-'))
        print(self.trigger_data)
        if self.trigger_data.get('trigger_id') == None:
            if self.trigger_data.get('msg'):
                print(self.trigger_data.get('msg'))
            else:
                print("\033[41;1m Invalid trigger data %s\033[0m" % self.trigger_data)
        else:
            trigger_id = self.trigger_data.get('trigger_id')
            host_id = self.trigger_data.get('host_id')
            trigger_obj = models.Trigger.objects.get(id = trigger_id)
            actions_set = trigger_obj.action_set.select_related()
            matched_action_list = set()
            for action in actions_set:
                for hg in action.host_groups.select_related():
                    for h in hg.host_set.select_related():
                        if h.id == host_id:
                            matched_action_list.add(action)
                            if action.id not in self.alert_counter_dic:
                                self.alert_counter_dic[action] = {h.id:{'counter':0,'last_alert':time.time()}}
                for host in action.hosts.select_related():
                    if host.id == host_id:
                        matched_action_list.setdefault(action,{host.id:{'counter':0,'last_alert':time.time()}})
            for action_obj in matched_action_list:
                if time.time() - self.alert_counter_dic[action_obj][host_id]['last_alert']
                    for action_operation in action_obj.operations.select_related():
                        if action_operation > self.alert_counter_dic[action_obj][host_id]:
                            print("alert action:%s" % action.actione_type,action.notifiers)