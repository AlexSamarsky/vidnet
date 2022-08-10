# from server.users.models import User
from users.services import user_create_superuser

user_create_superuser(email='xxx@yandex.ru', password='123',
                      first_name='xxx', last_name='xxx')
