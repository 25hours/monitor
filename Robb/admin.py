from django.contrib import admin
from Robb import models
# Register your models here.

class HostAdmin(admin.ModelAdmin):
    list_display = ('id','ip_addr','status')
    filter_horizontal = ('host_group','templates')

class TemplateAdmin(admin.ModelAdmin):
    filter_horizontal = ('services','triggers')

class ServiceAdmin(admin.ModelAdmin):
    filter_horizontal = ('items',)
    list_display = ('name','interval','plugin_name')

class TriggerExpressionInline(admin.ModelAdmin):
    model = models.TriggerExpression

class TriggerAdmin(admin.ModelAdmin):
    list_display = ('name','severity','enabled')
    inlines = [TriggerExpressionInline]

class TriggerExpressionAdmin(admin.ModelAdmin):
    list_display = ('trigger','service','service_index','specified_index_key')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','name','phone','weixin','email')

admin.site.register(models.Host,HostAdmin)
admin.site.register(models.HostGroup)
admin.site.register(models.Template,TemplateAdmin)
admin.site.register(models.Service,ServiceAdmin)
admin.site.register(models.Trigger,TriggerAdmin)
admin.site.register(models.TriggerExpression,TriggerExpressionAdmin)
admin.site.register(models.ServiceIndex)
admin.site.register(models.Action)
admin.site.register(models.ActionOperation)
admin.site.register(models.Maintenance)
