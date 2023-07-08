from deta import Deta
from pprint import pprint
import streamlit as st


DETA_KEY = st.secrets.DETA_KEY
deta = Deta(DETA_KEY)


sl = deta.Base("sl")
recipes = deta.Base("recipes")


#---SHOPPING LIST FUNCTIONS---#


def enter_shopping_list_items(weeknumber, title, shopping_list):
    """This function will add all items in the shopping_list dictionary and the week title to the database with the week number as a key. Will return None if successful. """
    return sl.put({"key":str(weeknumber),"title":title, "shopping_list":shopping_list})


def get_shopping_list(period):
    """Returns the entire shopping list item for a certain week based on the period. This period is the week title used in the function above."""
    return sl.get(str(period))


def update_shopping_list(weeknumber, update_dict):
    """Updating values in Deta Base only takes the key of the items you already created  and a dictionary of key-value pairs that can add, modify or delete the original data in the database."""
    for key, value in update_dict.items():
        print(f"{key} {value} ")
        shopping_list_update_line = {
            f"shopping_list.{key}.items": sl.util.append(value)
            }
           
        sl.update(shopping_list_update_line, weeknumber)


def remove_item_shopping_list(weeknumber, item_cat, item_to_remove):
    """Function  to remove a single item from the list. It takes a weeknumber as the principal key to get the list for the correct week. The item_cat selects the category and the item_to_remove is the actual item to get rid off. The same update function as above is then used to apply the changes."""
    shopping_list_to_change = get_shopping_list(weeknumber)["shopping_list"][item_cat]['items']
    shopping_list_to_change.remove(item_to_remove)
    print(shopping_list_to_change)
   
    shopping_list_update_line = {
        f"shopping_list.{item_cat}.items": shopping_list_to_change
        }


    sl.update(shopping_list_update_line, weeknumber)


#---RECIPE FUNCTIONS


def get_recipes():
    """Calling the fetch method from Deta to retrieve all recipes from the database."""
    return recipes.fetch().items


def enter_recipe(name, ingredients, instructions, active=False):
    """Using the Deta put method with the recipe name as the key, this function inserts the ingredients and instructions into the database.
    The default False value for the active parameter will be used to determine if the recipe is in this week’s column or not."""
    return recipes.put({"key" : name,"ingredients" : ingredients, "instructions" :instructions, "active" : active})


def get_recipe_status(col_nr = "a"):
    """A function to easily get the status of a recipe and append it to the correct list used in the shopping_list.py file. The col_nr parameter is used to determine the column a recipe is placed into."""
    needed_recipe_list = []
    if col_nr =="a":
        for recipe in get_recipes():
            if recipe["active"] == True:
                needed_recipe_list.append(recipe)
    elif col_nr =="b":
        for recipe in get_recipes():
            if recipe["active"] == False:
                needed_recipe_list.append(recipe)
    return needed_recipe_list


def update_recipe_status(key):
    """This function will change the boolean active variable and just inverts the current boolean status."""
    to_change= recipes.get(key)
    if to_change["active"] == False:
        changed = {"active" : True}
        recipes.update(changed, key)
    else:
        changed = {"active" : False}
        recipes.update(changed, key)


def add_ingredients_to_shopping_list(key, weeknumber):
    """This function will retrieve all the ingredients of the selected recipe and then call the Deta update method to add those ingredients to this week's shopping list"""
    ingredients_to_add= recipes.get(key)
    for ingredient in ingredients_to_add["ingredients"]:
        shopping_list_update_line = {
            "shopping_list.snacks.items": sl.util.append(ingredient.strip("-"))
            }
   
        sl.update(shopping_list_update_line, weeknumber)