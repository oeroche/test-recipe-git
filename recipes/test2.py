from harmony_client.runtime import recipe_main
from pydantic import BaseModel
from harmony_client.runtime import RecipeContext


class Config(BaseModel):
    name: str
    age: int


@recipe_main
def main(config: Config, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old. test")
