configs = {
    'HostID':2,
    'Server':'localhost',
    'ServerPort':8000,
    'urls':{
        'get_configs':['monitor/api/client/config','get'],
        'service_report':['monitor/api/client/service/report/','post'],
    }
    'RequestTimeout':30,
    'ConfigUpdateInterval':300
}