import json,time

class DataStore(object):
    '''
    processing the client reported service data , do some data optimize
    '''
    def __init__(self,client_id,service_name,data,redis_obj):
        '''

        :param client_id:
        :param service_name:
        :param data:
        :param redis_obj:
        '''
        self.client_id = client_id
        self.service_name = service_name
        self.data = data
        self.redis_conn_obj = redis_obj
        self.process_and_save()

    def get_data_slice(self,lastest_data_key,optimization_interval):
        '''

        :param lastest_data_key:
        :param optimization_interval:
        :return:
        '''
        all_real_data = self.redis_conn_obj.lrange(lastest_data_key,1,-1)
        data_set = []
        for item in all_real_data:
            data = json.loads(item.decode())
            if len(data) == 2:
                service_data,last_save_time =data
                if time.time() - last_save_time <= optimization_interval:
                    data_set.append(data)
                else:
                    pass
        return data_set

    def process_and_save(self):
        '''
        processing data and save into redis
        :return:
        '''
        print("\033[42;1m---service data -------\033[0m")
        if self.data['status'] == 0:
            for key,data_series_val in settings.STATUS_DATA_OPTIMIZATION.items():
                data_series_key_in_redis = "StatusData_%s_%s_%s" %(self.client_id,self.service_name,key)
                last_point_from_redis = self.redis_conn_obj.lrange(data_series_key_in_redis,-1,-1)
                if not last_point_from_redis:   #this key is not exist in redis
                    #so initialize a new key ,the first data point in the data set will only be used to identify that when
                    #was the data got saved last time
                    self.redis_conn_obj.rpush(data_series_key_in_redis,json.dumps([None,time.time()]))
                if data_series_val[0] == 0: #this dataset is for unoptimiaed data,only the latest data no need optimization
                    self.redis_conn_obj.rpush(data_series_key_in_redis,json.dumps([self.data,time.time()]))
                else:
                    last_point_data,last_point_save_time = json.loads(self.redis_conn_obj.lrange(data_series_key_in_redis,-1,-1)[0].decode())
                    if time.time() - last_point_save_time >= data_series_val[0]:
                        lastest_data_key_in_redis = "StatusData_%s_%s_latest" %(self.client_id,self.service_name)
                        print("calculating data for key:\033[31;1m%s\033[0m" %data_series_key_in_redis)
                        data_set = self.get_data_slice(lastest_data_key_in_redis,data_series_val[0])
                        print("------------------------len dataset:",len(data_set))
                        if len(data_set) > 0:
                            optimized_data = self.get_optimized_data(data_series_key_in_redis,data_set)
                            if optimized_data:
                                self.save_optimized_data(data_series_key_in_redis,optimized_data)

    def get_optimized_data(self,data_set_key,raw_service_data):
        '''
        calculate out avg,max,nin.mid value from raw service data set
        :param data_set_key:
        :param raw_service_data:
        :return:
        '''
        print("get_optimized_data:",raw_service_data[0])
        service_data_keys = raw_service_data[0] [0].keys()
        first_service_data_point = raw_service_data[0] [0]
        optimized_dic = {}  #save the optimized data
        if 'data' not in service_data_keys:
            for key in service_data_keys:
                optimized_dic[key] = []
            tmp_data_dic = copy.deepcopy(optimized_dic)
            for service_data_item,last_save_time in raw_service_data:
                for service_index,v in service_data_item.items():
                    try:
                        tmp_data_dic[service_index].append(round(float(v),2))
                    except ValueError as e:
                        pass
            for service_k,v_list in tmp_data_dic.items():
                print(service_k,v_list)
                avg_res = self.get_average(v_list)
                max_res = self.get_max(v_list)
                min_res = self.get_min(v_list)
                mid_res = self.get_mid(v_list)
                optimized_dic[service_k] = [avg_res,max_res,min_res,mid_res]
                print(service_k,optimized_dic[service_k])
        else:
            for service_item_key,v_dic in first_service_data_point['data'].items():
                optimized_dic[service_item_key] = {}
                for k2,v2 in v_dic.items():
                    optimized_dic[service_item_key][k2] = []
            tmp_data_dic =copy.deepcopy(optimized_dic)
            if tmp_data_dic:
                print("tmp data dic:",tmp_data_dic)
                for service_data_item,last_save_time in raw_service_data:
                    for service_index,val_dic in service_data_item['data'].items():
                        for service_item_sub_key,val in val_dic.items():
                            tmp_data_dic[service_index][service_item_sub_key].append(round(float(val),2))
                for service_k,v_dic in tmp_data_dic.items():
                    for service_item_sub_key,v_list in v_dic.items():
                        print(service_k,service_sub_k,v_list)
                        avg_res = self.get_average(v_list)
                        max_res = self.get_max(v_list)
                        min_res = self.get_min(v_list)
                        mid_res = self.get_mid(v_list)
                        optimized_dic[service_k][service_sub_k] = [avg_res, max_res, min_res, mid_res]
                        print(service_k, service_sub_k, optimized_dic[service_k][service_sub_k])
            else:
                print("\033[41;1mMust be sth wrong with client report data\033[0m")
        print("optimized empty dic:",optimized_dic)
        return optimized_dic
    def get_average(self,data_set):
        if len(data_set) > 0:
            return sum(data_set)//len(data_set)
        else:
            return 0
    def get_max(self,data_set):
        if len(data_set) > 0:
            return max(data_set)
        else:
            return 0
    def get_min(self,data_set):
        if len(data_set) > 0:
            return min(data_set)
        else:
            return 0
    def get_mid(self,data_set):
        data_set.sort()
        if len(data_set) > 0:
            return data_set[len(data_set)//2]
        else:
            return 0
