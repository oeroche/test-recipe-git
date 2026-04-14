from harmony_client.runtime import recipe_main, InputConfig
from pydantic import InputConfig
from harmony_client.runtime import RecipeContext


class ConfigBis(InputConfig):
    country: str
    size: int


@recipe_main(name="great recipe", description="a great recipe")
def great_recipe(config: ConfigBis, ctx: RecipeContext):
    print(f"Hello user from {config.country}! You are {config.int} tall.")
