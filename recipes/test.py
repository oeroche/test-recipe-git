from harmony_client.runtime import recipe_main, InputConfig
from pydantic import BaseModel
from harmony_client.runtime import RecipeContext


class Config(InputConfig):
    name: str
    age: int


@recipe_main
def main(config: Config, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old. test")


@recipe_main(name="other recipe",description="oh yeah")
def other(config: Config, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old. test")
