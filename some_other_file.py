from harmony_client.runtime import recipe, InputConfig, Dataset, dataset_kinds, Field
from harmony_client.runtime import RecipeContext
from typing import Annotated


class ConfigBis(InputConfig):
    name: str
    age: int
    dataset: Annotated[
        Dataset[dataset_kinds.Prompt],
        Field(description="Dataset to evaluate on", title="Dataset"),
    ]


@recipe(
    name="outside of recipe folder recipe",
    description="a recipe outside of the recipe folder",
)
def outside_of_recipe_folder(config: ConfigBis, ctx: RecipeContext):
    print(f"Hello {config.name}! You are {config.age} years old.")
