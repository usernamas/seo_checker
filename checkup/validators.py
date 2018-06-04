from django.core.validators import URLValidator
from django.core.validators import ValidationError
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import MissingSchema

def validate_url(value):
    url_validator = URLValidator()
    value_1_invalid = False
    value_2_invalid = False

    try:
        url_validator(value)
    except:
        value_1_invalid = True

    value_2_url = "http://" + value
    try:
        url_validator(value_2_url)
    except:
        value_2_invalid = True

    if value_1_invalid == True and value_2_invalid == True:
        raise ValidationError("Invalid URL for this field")
    else:
        return value

def url_exists(value):
    try:
        request = requests.get(value)
    except ConnectionError:
        raise ValidationError("Website does not exist")
    except MissingSchema:
        raise ValidationError("Website does not exist")
    except:
        raise ValidationError("Website does not exist")
    else:
        return value
