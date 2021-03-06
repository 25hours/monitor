from django.shortcuts import render,HttpResponse
import json
from monitor import settings
from Robb.backends import redis_conn
from Robb.backends import data_processing
from Robb.backends import data_optimization
from Robb.serializer import ClientHandler,get_host_triggers
from django.views.decorators.csrf import csrf_exempt
from Robb import models

# Create your views here.
REDIS_OBJ = redis_conn.redis_conn(settings)
def dashboard(request):

    return render(request,'Robb/monitor/dashboard.html')
def triggers(request):

    return render(request,'Robb/monitor/triggers.html')
def index(request):
    return render(request,'Robb/monitor/index.html')
def hosts(request):
    host_list = models.Host.objects.all()
    print("hosts:",host_list)
    return render(request,'Robb/monitor/hosts.html',{'host_list':host_list})
def host_detail(request,host_id):
    host_obj = models.Host.objects.get(id=host_id)
    return render(request,'Robb/monitor/host_detail.html',{'host_obj':host_obj})
def trigger_list(request):

    host_id = request.GET.get("by_host_id")

    host_obj = models.Host.objects.get(id=host_id)

    alert_list = host_obj.eventlog_set.all().order_by('-date')
    return render(request,'Robb/monitor/trigger_list.html',locals())
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
            print('host=%s,service=%s' %(request.POST.get('client_id'),request.POST.get('service_name')))
            data = json.loads(request.POST['data'])
            client_id = request.POST.get('client_id')
            service_name = request.POST.get('service_name')
            #优化存储
            data_saveing_obj = data_optimization.DataStore(client_id,service_name,data,REDIS_OBJ)
            #触发监控
            host_obj = models.Host.objects.get(id=client_id)
            service_triggers = get_host_triggers(host_obj)

            trigger_handler = data_processing.DataHandler(settings,connect_redis=False)
            for trigger in service_triggers:
                trigger_handler.load_services_data_and_calulating(host_obj,trigger,REDIS_OBJ)
            print("service trigger::",service_triggers)

        except IndexError as e:
            print("---->err:",e)
    return HttpResponse(json.dumps("----report success----"))