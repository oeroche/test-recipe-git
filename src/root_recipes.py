from harmony_client.runtime import recipe, InputConfig
from harmony_client.runtime import RecipeContext


class MyConfig(InputConfig):
    name: str
    age: int


class MyOtherConfig(InputConfig):
    country: str
    size: int

@recipe(name="My Main Recipe", description="The main recipe")
def main(config: MyOtherConfig, ctx: RecipeContext):
    print(f"Hello user from {config.country}! You are {config.int} tall.")
