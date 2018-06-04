from django import template
import json
import html

register = template.Library()
speed_messages = {}

@register.filter()
def get_type(value):
    return type(value).__name__

@register.filter()
def format_args(str, args):

    for arg in args:
        str = str.replace('{{' + arg['key'] + '}}', arg['value'])

        if arg['key'] == 'LINK' and arg['type'] == 'HYPERLINK':
            str = str.replace('{{BEGIN_LINK}}', "<a href='" + arg['value'] + "'>")
            str = str.replace('{{END_LINK}}', '</a>')
    return str

@register.filter()
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter()
def load_json(data):
    pass
    #return json.loads(data)

@register.filter()
def speed_data(value, key):
    if key not in speed_messages:
        speed_messages[key] = []
        speed_messages[key].append(value)
    return value

@register.filter()
def get_speed_data():
    return json.dumps(speed_messages)

@register.filter()
def get_iterations(data):
    list = []
    for i in range(len(data)):
        list += i
    return list
