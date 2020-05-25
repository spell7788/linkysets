from model_bakery.recipe import Recipe, foreign_key

from polemicflow.entries.tests.bakery_recipes import entryset_recipe

reply_recipe = Recipe(
    "entries.Reply", set=foreign_key(entryset_recipe), lft=None, rght=None, level=None,
)
