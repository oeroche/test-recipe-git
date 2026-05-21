from harmony_client.runtime import recipe, InputConfig
from harmony_client.runtime import RecipeContext


class MyConfig(InputConfig):
    name: str
    age: int


@recipe(
    name="A recipe from the new branch",
    description="A new recipe has been created",
)
def new_recipe(config: MyConfig, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old from a new recipe")
