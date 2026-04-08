from model import Model
from field import CharField, IntegerField, EmailField

class User(Model):
    name = CharField(max_length=100)
    email = EmailField(max_length=255)
    age = IntegerField(nullable=True)

User.create_table()
print(User.read_all())
print(User.read_one(name="Alice"))

# create
# alice = User(name="Alice", email="alice@example.com", age=30)
# alice.save()

## update
# alice.update(email="alice@gmail.com")
#
## delete
# alice.delete()
