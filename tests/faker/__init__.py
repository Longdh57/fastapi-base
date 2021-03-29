import faker.providers

from tests.faker.user_provider import UserProvider

fake = faker.Faker()

fake.add_provider(UserProvider)
