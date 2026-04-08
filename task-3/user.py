from model import Model
from field import CharField, IntegerField, EmailField

class User(Model):
    name = CharField(max_length=100)
    email = EmailField(max_length=255, unique=True)
    age = IntegerField(nullable=True)

User.create_table()

# create
alice = User(name="Alice", email="alice@example.com", age=30)
alice.save()

alice_2 = User(name="Alice", email="alice@gmail.com", age=30)
alice_2.save()

# read
print(f"\n{User.read_all()}")
print(f"\n{User.read(email="alice@gmail.com")}")

# update
alice.update(email="alice@gmail.in")

# delete
alice.delete()
print(f"\n{User.read_all()}")
