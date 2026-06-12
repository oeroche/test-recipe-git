from harmony_client.parameters import Grader
from harmony_client.runtime import recipe, InputConfig
from harmony_client.runtime import RecipeContext
from common.common import operate_on_data
from typing import Annotated
from pydantic import Field


class SumConfig(InputConfig):
    data: list[int]
    grader: Annotated[
        Grader,
        Field(description="List of graders to evaluate models with.", title="Graders"),
    ]


@recipe(name="average", description="Get the average of a list of numbers")
async def average(config: SumConfig, ctx: RecipeContext):
    grader = await config.grader.load(ctx)
    print("selected grader: ", grader.grader_key)
    print(f"The average of the data is {operate_on_data(config.data, 'average')}")
