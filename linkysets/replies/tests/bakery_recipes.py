from model_bakery.recipe import Recipe, foreign_key

from linkysets.entries.tests.bakery_recipes import entryset_recipe

reply_recipe = Recipe(
    "replies.Reply", entryset=foreign_key(entryset_recipe), lft=None, rght=None, level=None,
)
