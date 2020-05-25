from model_bakery.recipe import Recipe, foreign_key, related

from polemicflow.users.tests.bakery_recipes import user_recipe

entry_recipe = Recipe("entries.Entry")

entryset_recipe = Recipe(
    "entries.EntrySet",
    author=foreign_key(user_recipe),
    entries=related(entry_recipe, entry_recipe),
)

reply_recipe = Recipe(
    "entries.Reply", set=foreign_key(entryset_recipe), lft=None, rght=None, level=None,
)
