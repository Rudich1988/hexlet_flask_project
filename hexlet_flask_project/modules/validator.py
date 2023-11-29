def validate(data):
    errors = {}
    if not data['name']:
        errors['name'] = "Can't be blank"
    if len(data['name']) < 4:
        errors['name'] = 'Nickname must be greater than 4 characters'
    if not data['email']:
        errors['email'] = "Can't be blank"
    return errors
