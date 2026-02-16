from .templatetags.animal_filters import age

def generate_qr_text(animal):

    age_str = age(animal.birth_date)
    
    qr_text = f"Name: {animal.name}\n"
    qr_text += f"Species: {animal.species.name if animal.species else 'Unknown'}\n"
    qr_text += f"Breed: {animal.breed.name if animal.breed else 'Unknown'}\n"
    qr_text += f"Age: {age_str}\n"
    qr_text += f"Health: {animal.health_status}\n"
    if animal.chip_number:
        qr_text += f"Chip: {animal.chip_number}"
        
    return qr_text


