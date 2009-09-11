from random import randint

from django import template

from main.models import Nugget

register = template.Library()

def get_nugget():
    """ Grab and display a random fact nugget

    """
    nuggets = Nugget.objects.filter(
        active=True,
        )

    if not nuggets:
        nugget = """
I'm sorry.  I could not find any active facts in the database."""

    else:
        nugget = randint(0, len(nuggets) - 1)

        try:
            nugget = nuggets[nugget].text
        except IndexError:
            nugget = """
I'm sorry.  I've run into an error retrieving this BMC Fact."""
    
    return nugget

register.simple_tag(get_nugget)
