from harmony_client.runtime import recipe, InputConfig
from harmony_client.runtime import RecipeContext
from common.common import operate_on_data


class SumConfig(InputConfig):
    data: list[int]


@recipe(name="sum", description="A recipe I named")
def other(config: SumConfig, ctx: RecipeContext):
    print(f"The sum of the data is {operate_on_data(config.data, 'sum')}")
