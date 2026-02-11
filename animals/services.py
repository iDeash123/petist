

def generate_qr_code(animal):
    """
    Generate a QR code for the given animal instance.
    """
    pass

def calculate_age(birth_date):
    """
    Calculate current age based on birth date.
    """
    from django.utils import timezone
    if not birth_date:
        return None
    today = timezone.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
