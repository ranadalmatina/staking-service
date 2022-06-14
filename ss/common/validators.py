from django.core.exceptions import ValidationError


def validate_positive(value):
    if value < 0:
        raise ValidationError('Must be a positive number.', code='positive')


def validate_p_or_c(value: str):
    if value != 'P' or value != 'C':
        raise ValidationError("Only 'P' or 'C' allowed.")
