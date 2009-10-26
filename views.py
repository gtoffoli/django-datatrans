from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

from datatrans import utils
from datatrans.models import KeyValue

def model_list(request):
    registry = utils.get_registry()

    default_lang = utils.get_default_language()
    def _unedited_count(entry):
        keyvalues = KeyValue.objects.for_model(*entry).exclude(language=default_lang).filter(edited=False)
        return keyvalues.count()

    models = [(i, u'%s' % registry[i][0]._meta.verbose_name, registry[i][1].fields, _unedited_count(registry[i])) for i in range(len(registry))]

    languages = [l for l in settings.LANGUAGES if l[0] != default_lang]

    context = {'models': models, 'languages': languages}

    return render_to_response('datatrans/model_list.html', context, context_instance=RequestContext(request))

def model_detail(request, index, language):
    '''
    The context structure is defined as follows:

    context = {'model': '<name of model>',
               'fields': {'name': '<name of field>',
                          'items': [{'original': '<KeyValue object with original value>',
                                     'translations': [<KeyValue objects with translation>]}]
                         }
              }
    '''
    try:
        entry = utils.get_registry()[int(index)]
    except:
        raise Http404(u'No registered model found for given index.')

    default_lang = utils.get_default_language()
    model_name = u'%s' % entry[0]._meta.verbose_name
    fields = []
    for field in entry[1].fields:
        items = []
        objects = entry[0].objects.all()
        for object in objects:
            original = KeyValue.objects.get_keyvalue(object.__dict__[field], default_lang)
            translation = KeyValue.objects.get_keyvalue(object.__dict__[field], language)
            items.append({'original': original, 'translation': translation})
        fields.append({'name': field, 'items': items})


    context = {'model': model_name,
               'fields': fields,
               'original_language': default_lang,
               'other_language': language}


    return render_to_response('datatrans/model_detail.html', context, context_instance=RequestContext(request))

def make_messages(request):
    utils.make_messages()
    return HttpResponseRedirect(reverse('datatrans_model_list'))
