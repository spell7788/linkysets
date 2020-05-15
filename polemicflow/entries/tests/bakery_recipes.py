from model_bakery.recipe import Recipe, foreign_key

from polemicflow.users.tests.bakery_recipes import user_recipe

entry_recipe = Recipe("entries.Entry", _author=foreign_key(user_recipe))

anonymous_entry_recipe = entry_recipe.extend(_author=None)

reply_recipe = Recipe(
    "entries.Reply",
    entry=foreign_key(anonymous_entry_recipe),
    lft=None,
    rght=None,
    level=None,
)
