from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.context import RequestContext

from django.contrib.admin.views.decorators import staff_member_required

def edit(request):
    return None
