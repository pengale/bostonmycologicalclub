""" Walk Manipulation Tools """

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from forms import WalkForm, WalkMushroomForm
from models import Walk
from django.contrib.auth.models import User
from views import error_404, halt

def view_walklist(request):
    """ Lists all walks. """
    walk_list = Walk.objects.all()
    template = 'walklist.html'

    ctxt = { 
        'walk_list' : walk_list, 
        'request' : request,
}
    return render_to_response(template, ctxt)

def create_walk(request):
    """ View to create a new walk.  """

    if request.method == 'POST':
        form = WalkForm(request.POST)
        if form.is_valid():
            walk = form.save(commit=False)
            walk.creator = request.user
            walk.save()
            form.save_m2m()
            return HttpResponseRedirect('/walks/list/')
                
        else:
            form = WalkForm(request.POST)
            template = 'edit_walk.html'
            ctxt = { 'form' : form,  'request' : request }
            return render_to_response(template, ctxt)

    else:
        form = WalkForm(initial={ 
                'creator' : User.objects.get(username=request.user).id
                })
        template = 'edit_walk.html'
        ctxt = { 
            'form' : form,  
            'request' : request, 
            'walk' : None,
            }
        return render_to_response(template, ctxt)

def edit_walk(request, walk=None):
    """ Edit an existing walk. """
    if not walk:
        return create_walk(request)

    try:
        walk = Walk.objects.get(id=walk)
        if request.user.id != walk.creator.id:
            if not request.user.is_superuser:
                error = "You do not have permission to edit this walk."
                return halt(request, error)

    except ObjectDoesNotExist:
        error = "That walk does not appear to exist"
        return error_404(request, error)

    if request.method == 'POST':

        form = WalkForm(request.POST, instance=walk)

        if form.is_valid():
            walk = form.save(commit=False)
            walk.creator = request.user
            walk.save()
            form.save_m2m()
            return HttpResponseRedirect('/walks/list')

        else:
            form = WalkForm(request.POST)
            template = 'edit_walk.html'
            ctxt = { 'form' : form, 'request' : request }
            return render_to_response(template, ctxt)

    else:
        form = WalkForm(instance=walk)
        template = 'edit_walk.html'
        ctxt = { 
            'form' : form,  
            'request' : request,
            'walk' : walk,
            }
        return render_to_response(template, ctxt)

def made_walk(request, walk):
    """ Returns a page telling us that we succesfully made a walk."""
    template = "madewalk.html"
    ctxt = { "walk" : walk,  'request' : request }
    return render_to_response(template, ctxt)

def mushrooms(request, walk):
    if not walk:
        error = "Please specify a walk"
        return error_404(request, error)

    try:
        walk = Walk.objects.get(id=walk)
        
    except ObjectDoesNotExist:
        error = "That walk does not appear to exist"
        return error_404(request, error)

    if request.method == 'POST':
        
        form = WalkMushroomForm(request.POST, instance=walk)

        if form.is_valid():
            walk = form.save()
            return HttpResponseRedirect(
                '/walks/view/' + str(walk.id) + '/'
                )

        else:
            form = WalkMushroomForm(request.POST)

    else:
        form = WalkMushroomForm(instance=walk)


    template = 'walk_mushrooms.html'
    ctxt = { 'form' : form, 'request' : request, 'walk' : walk }
    return render_to_response(template, ctxt)


def view_walk(request, walk):
    """ View details about a specific walk. """

 
    try: 
        walk = Walk.objects.get(id=walk)

        # Decide whether user has permission to view 'edit' link
        permission = False
        if request.user.id == walk.creator.id: permission = True

        template = "walk.html"
        ctxt = { 
            'walk' : walk, 
            'request' : request, 
            'permission' : permission 
            }
        return render_to_response(template, ctxt)

    except:
        error = "It appears that the walk you requested does not exist."
        template = "404.html"
        ctxt = { "error" : error, 'request' : request }
        return render_to_response(template, ctxt)
