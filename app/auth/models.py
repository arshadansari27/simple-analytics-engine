class User:

    def __init__(self, user_id, name, email, phone):
        self.id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        assert (email or phone) is not None
    
class Authorisation:

    def __init__(self, user_id, user_name, password, roles=[]):
        self.user_id = user_id
        self.user_name = user_name
        self.password = password
        self.roles = roles

    def match_password(self, password):
        return self.password == password # encrypt before checking


