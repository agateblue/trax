from django.forms import ValidationError


class HandleError(ValidationError):
    def __init__(self, *args, **kwargs):
        self.err_code = kwargs.pop('err_code')
        super().__init__(*args, **kwargs)
