from django.contrib import admin

from .models import Rule, Message

#admin.site.disable_action('delete_selected')

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    #can_delete = False
    classes = ['collapse']
    #readonly_fields = ['status']

    #def has_add_permission(self, request):
        #return False


class RuleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'category', 'description', 'priority']})
    ]
    #readonly_fields = ['name']
    #actions = None#['add_new', 'delete_selected']
    '''
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Category Information', {'fields': ['category'], 'classes': ['collapse']})
    ]
    '''
    inlines = [MessageInline]
    list_display = ('name', 'category', 'description', 'priority')
    list_filter = ['category', 'priority']
    search_fields = ['name', 'description']
    '''
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):  # note the obj=None
        return False
    '''

class MessageAdmin(admin.ModelAdmin):
    #actions = ['add_new', 'delete_selected']#None#['add_new', 'delete_selected']
    list_display = ('name', 'status', 'message')
    list_filter = ['status'] #, 'name']
    search_fields = ['name__name', 'message']
    #can_delete = False
    #readonly_fields = ['status']

    #def has_add_permission(self, request):
        #return False

    #def has_delete_permission(self, request, obj=None):  # note the obj=None
        #return False

admin.site.register(Rule, RuleAdmin)
admin.site.register(Message, MessageAdmin)
