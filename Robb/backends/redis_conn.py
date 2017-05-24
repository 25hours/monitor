import django
import redis

def redis_conn(django_settings):
    pool = redis.ConnectionPool(host=django_settings.REDIS_CONN['HOST'])
    r = redis.Redis(connection_pool=pool)
    return r