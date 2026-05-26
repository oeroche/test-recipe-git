from tracemalloc import get_traced_memory
from harmony_client.runtime import recipe, InputConfig
from harmony_client.runtime import RecipeContext


class MyConfig(InputConfig):
    name: str
    age: int


class MyOtherConfig(InputConfig):
    country: str
    size: int


@recipe(
    name="Nested Recipe",
    description="A nested recipe",
)
def other(config: MyOtherConfig, ctx: RecipeContext):
    print(f"Hello user from {config.country}! You are {config.int} tall.")
