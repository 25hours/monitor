import time,json,pickle
from monitor import settings
from Robb import models
from Robb.backends import redis_conn
import operator
import redis

class DataHandler(object):
    def __init__(self,django_settings,connect_redis=True):
        self.django_settings = django_settings
        self.poll_interval = 0.5
        self.config_update_interval =120
        self.config_last_loading_time = time.time()
        self.global_monitor_dic = {}
        self.exit_flag = False
        if connect_redis:
            self.redis = redis_conn.redis_conn(django_settings)

    def looping(self):
        self.update_or_load_configs()
        count = 0


    def load_services_data_and_calulating(self,host_obj):
        self.redis = redis_obj
        calc_sub_res_list = []
        positive_expressions = []
        expression_res_string = ''
        for expression in trigger_obj.triggerexpression_set.select_related().order_by('id'):
            print(expression,expression.logic_type)
            expression_process_obj = ExpressionProcess(self,host_obj,expression)
            single_expression_res = expression_process_obj.process()    #求单条表达式的结果
            if single_expression_res:
                calc_sub_res_list.append(single_expression_res)
                if single_expression_res['expression_obj'].logic_type:
                    expression_res_string += str(single_expression_res['calc_res']) + ' ' + \
                                             single_expression_res['expression_obj'].logic_type + ' '
                else:
                    expression_res_string += str(single_expression_res['calc_res']) + ' '
                #把所欲结果为True的expression提出来，报警时知道是谁出的问题导致trigger触发
                if single_expression_res['calc_res'] == True:
                    single_expression_res['expression_obj'] = single_expression_res['expression_']
                    positive_expressions.append(single_expression_res)
        print("whole trigger res:",trigger_obj.name,expression_res_string)
        if expression_res_string:
            trigger_res = eval(expression_res_string)
            print("whole trigger res:",trigger_res)
            if trigger_res:
                print("#######trigger alert:",trigger_obj.severity,trigger_res)
                self.trigger_notifier(host_obj,trigger_obj.id,positive_expressions,msg=trigger_obj.name)
    def updata_or_load_configs(self):

class ExpressionProcess(object):
    def __init__(self,main_ins,host_obj,expression_obj,specified_item=None):
        '''
        :param main_ins: DataHandler 实例
        :param host_obj: 具体的host obj
        :param expression_obj:
        :param specified_item:
        '''
        self.host_obj = host_obj
        self.expression_obj = expression_obj
        self.main_ins = main_ins
        self.services_redis_key = "StatusData_%s_%s_latest" %(host_obj.id,expression_obj.service.name)
        self.time_range = self.expression_obj.data_calc_args.split(',')[0]  #拼出此服务在redis存储中对应的key
        print("\033[31:1m---->%s\033[0m" % self.services_redis_key) #获取要从redis中取多长时间的数据，单位minute
    def load_data_from_redis(self):
        time_in_sec = int(self.time_range) * 60
        approximate_data_points = (time_in_sec + 60) / self.expression_obj.service.interval
        print("approximate dataset nums:",approximate_data_points,time_in_sec)
        data_range_raw = self.main_ins.redis.lrange(self.services_redis_key,-approximate_data_points,-1)
        approximate_data_range = [json.loads(i.decode()) for i in data_range_raw]
        data_range = []
        for point in approximate_data_range:
            val,saving_time = point
            if time.time() - saving_time < time_in_sec:
                data_range.append(point)
        print(data_range)
        return data_range
    def process(self):
        data = self.load_data_from_redis()
        data_calc_func = getattr(self,'get_%s' % self.expression_obj.data_calc_func)
        single_expression_calc_res = data_calc_func(data)
        print("---res of single_expression_calc_res",single_expression_calc_res)
        if single_expression_calc_res:  #确保上面的条件，有正确的返回
            res_dic = {
                'calc_res':single_expression_calc_res[0],   #True or False
                'calc_res_val':single_expression_calc_res[1],
                'expression_obj':self.expression_obj,
                'service_item':single_expression_calc_res[2],
            }
            print("\033[41;1m single_expression_calc_res:%s\033[0m")
            return res_dic
        else:
            return False
    def get_avg(self,data_set):
        clean_data_list = []
        clean_data_dic = {}
        for point in data_set:
            val,save_time = point
            if val:
                if 'data' not in val:
                    clean_data_list.append(val[self.expression_obj.service_index.key])
                else:
                    for k,v in val['data'].items():
                        if k not in clean_data_dic:
                            clean_data_dic[k] = []
                        clean_data_dic[k].append(v[self.expression_obj])
        if clean_data_list:
            clean_data_list = [float(i) for i in clean_data_list]
            avg_res = sum(clean_data_list)/len(clean_data_list)
            print("\033[46;1m---avg res:%s\033[0m" % avg_res)
            return [self.judge(avg_res),avg_res,None]
        elif clean_data_dic:
            for k,v in clean_data_dic.items():
                clean_v_list = [float(i) for i in v]
                avg_res =0 if sum(clean_v_list) == 0 else sum()
                print("\033[46;1m-%s---avg res:%s\033[0m")

    def judge(self,calculated_val):
        calc_func = getattr(operator,self.expression_obj.operator_type)
        return calc_func(calculated_val,self.expression_obj.th)

    def trigger_notifier(self,host_obj,trigger_id,positive_expression,redis_obj):
        '''

        :param host_obj:
        :param trigger_id:
        :param positive_expression:
        :param redis_obj:
        :return:
        '''
        if redis_obj:
            self.redis = redis_obj
        print("\033[43;1m going to send alert msg ....\033[0m")
        print("trigger_notifier agv:",host_obj,trigger_id,positive_expression)
        msg_dic = {
            'host_id':host_obj.id,
            'trigger_id':trigger_id,
            'positive_expressions':positive_expression,
            'msg':msg,
            'time':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
            'start_time':time.time(),
            'duration':None
        }
        self.redis.publish(self.django_settings,TRIGGER_CHAN,pickle.dumps(msg_dic))