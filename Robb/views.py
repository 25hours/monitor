from django.shortcuts import render,HttpResponse
import json
from monitor import settings
from Robb.backends import redis_conn
from Robb.backends import data_optimization
from Robb.serializer import ClientHandler,get_host_triggers
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
REDIS_OBJ = redis_conn.redis_conn(settings)
def client_configs(requset,client_id):
    print("--->",client_id)
    config_obj = ClientHandler(client_id)
    config = config_obj.fetch_configs()
    if config:
        return HttpResponse(json.dump(config))

@csrf_exempt
def service_data_report(request):
    if request.method == 'POST':
        print("---->",request.POST)
        try:
            print('host=%s,service=%s' %(request.POST.get('client_id')))
            data = json.loads(request.POST['data'])
            client_id = request.POST.get('client_id')
            service_name = request.POST.get('service_name')
            #优化存储
            data_saveing_obj = data_optimization.DataStore(client_id,service_name,data,REDIS_OBJ)
            #触发监控
            host_obj = models.Host.objects.get(id=client_id)
            service_triggers = get_host_triggers(host_obj)

            trigger_handler = data_processing.DataHandler(settings)
            for trigger in service_triggers:
                trigger_handler.load_services_data_and_calulating()
            print("service trigger::",service_triggers)

        except IndexError as e:
            print("---->err:",e)
    return HttpResponse(json.dumps("----report success----"))