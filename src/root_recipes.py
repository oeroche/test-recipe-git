from harmony_client.runtime import recipe, InputConfig
from harmony_client.runtime import RecipeContext


class MyConfig(InputConfig):
    name: str
    age: int


class MyOtherConfig(InputConfig):
    country: str
    size: int


@recipe
def main(config: MyConfig, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old.")


@recipe(name="My named Recipe", description="A recipe I named")
def other(config: MyOtherConfig, ctx: RecipeContext):
    print(f"Hello user from {config.country}! You are {config.int} tall.")
