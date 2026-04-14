from harmony_client.runtime import recipe_main, InputConfig
from pydantic import BaseModel
from harmony_client.runtime import RecipeContext


class Config(InputConfig):
    name: str
    age: int

class ConfigBis(InputConfig):
    country: str
    size: int


@recipe_main
def main(config: ConfigBis, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old.")


@recipe_main(name="other recipe",description="oh yeah")
def other(config: ConfigBis, ctx: RecipeContext):
    print(f"Hello user from {config.country}! You are {config.int} tall.")
