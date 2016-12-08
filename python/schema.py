# -*- coding:utf-8 -*-
import datetime
import random

import graphene
from graphql.language import ast


class DateTime(graphene.Scalar):
    """
    DateTime Scalar Description
    Format: %Y-%m-%dT%H:%M:%S.%f
    """

    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(
                node.value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")


class Gender(graphene.Enum):
    MALE = 'male'
    FEMALE = 'female'


class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    age = graphene.Float()
    gender = graphene.Field(Gender)
    created_at = DateTime()


class Character(graphene.Interface):
    name = graphene.String()


class Human(graphene.ObjectType):
    class Meta:
        interfaces = (Character, )

    gender = graphene.Field(Gender)


class Droid(graphene.ObjectType):
    class Meta:
        interfaces = (Character, )

    function = graphene.String()


genders = [Gender.MALE.value, Gender.FEMALE.value]
users = [
    User(
        id=i,
        name='user {0}'.format(i),
        age=i*10,
        gender=random.choice(genders),
        created_at=datetime.datetime.utcnow()
    )
    for i in range(1, 11)
]
humans = [
    Human(
        name='human {0}'.format(i),
        gender=random.choice(genders)
    )
    for i in range(1, 11)
]
droids = [
    Droid(
        name='droid {0}'.format(i),
        function='function {0}'.format(i)
    )
    for i in range(1, 11)
]
last_user_id = 10


class CreateUser(graphene.Mutation):

    class Input:
        name = graphene.Argument(graphene.String, required=True)
        age = graphene.Argument(graphene.Int, required=True)
        gender = graphene.Argument(Gender, required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    def mutate(self, args, context, info):
        global last_user_id, users

        _id = last_user_id + 1
        u = User(
            id=_id,
            name=args.get('name'),
            age=args.get('age'),
            gender=args.get('gender'),
            created_at=datetime.datetime.utcnow()
        )
        last_user_id = _id
        users.append(u)
        return CreateUser(user=u, ok=True)


class UserInput(graphene.InputObjectType):
    id = graphene.Field(graphene.ID, required=True)
    name = graphene.Field(graphene.String)
    age = graphene.Field(graphene.Int)
    gender = graphene.Field(Gender)


class UpdateUser(graphene.Mutation):
    class Input:
        user_data = graphene.Argument(UserInput)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    def mutate(self, args, context, info):
        data = args.get('user_data')
        _id = data.pop('id')
        for u in users:
            if str(u.id) == _id:
                for k, v in data.items():
                    setattr(u, k, v)
                return UpdateUser(user=u, ok=True)
        return UpdateUser(user=None, ok=False)


class Query(graphene.ObjectType):

    user = graphene.Field(User, id=graphene.Int())
    users = graphene.List(lambda: User)
    human = graphene.Field(Human, name=graphene.String())
    droid = graphene.Field(Droid, name=graphene.String())

    def resolve_user(self, args, context, info):
        for u in users:
            if u.id == args.get('id'):
                return u

    def resolve_users(self, args, context, info):
        return users

    def resolve_human(self, args, context, info):
        for h in humans:
            if h.name == args.get('name'):
                return h

    def resolve_droid(self, args, context, info):
        for d in droids:
            if d.name == args.get('name'):
                return d


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
