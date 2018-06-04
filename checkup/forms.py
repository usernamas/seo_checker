from django import forms

from .validators import validate_url, url_exists

class SubmitUrlForm(forms.Form):
    url = forms.CharField(max_length=5000, label='Submit URL', validators=[validate_url, url_exists])
    #url = forms.URLField(max_length=200, help_text="input page URL", initial='http://', label='')
