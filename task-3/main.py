from model import Model
from field import CharField, IntegerField, EmailField, ForeignKey

class User(Model):
    name = CharField(max_length=100)
    email = EmailField(max_length=255, unique=True)
    age = IntegerField(nullable=True)

class Post(Model):
    title = CharField(max_length=200)
    author = ForeignKey(User, related_name="posts")

# creating tables
User.create_table()
Post.create_table()
print()

# create tuples
alice = User(name="Alice", email="alice@example.com", age=30)
alice.save() 

jake = User(name="Jake", email="jake@example.com", age=26)
jake.save()
print()

# filter and order by
users = User.filter(age__gte=25).order_by("-name").all()
print(users)
print()

# delete
jake.delete()
users = User.read_all()
print(users)
print()

# Relations
post = Post(title='Hello world',  author=alice)
post.save()
print()

print(alice.posts)
