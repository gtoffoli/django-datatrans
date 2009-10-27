from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType

from datatrans import utils
from datatrans.models import KeyValue

def _get_model_slug(model):
        ct = ContentType.objects.get_for_model(model)
        return u'%s.%s' % (ct.app_label, ct.model)

def _get_model_entry(slug):
    app_label, model_slug = slug.split('.')
    ct = ContentType.objects.get(app_label=app_label, model=model_slug)
    model_class = ct.model_class()
    registry = utils.get_registry()
    entry = [e for e in registry if e[0] == model_class]
    if len(entry) == 0:
        raise Http404(u'No registered model found for given query.')
    return entry[0]

def _get_model_stats(model, modeltranslation, filter=lambda x: x):
    default_lang = utils.get_default_language()
    keyvalues = filter(KeyValue.objects.for_model(model, modeltranslation).exclude(language=default_lang))
    total = keyvalues.count()
    done = keyvalues.filter(edited=True).count()
    return (done * 100 / total, done, total)


@staff_member_required
def model_list(request):
    registry = utils.get_registry()

    default_lang = utils.get_default_language()

    models = [(_get_model_slug(registry[i][0]),
               u'%s' % registry[i][0]._meta.verbose_name,
               registry[i][1].fields,
               _get_model_stats(*registry[i])) for i in range(len(registry))]

    languages = [l for l in settings.LANGUAGES if l[0] != default_lang]

    context = {'models': models, 'languages': languages}

    return render_to_response('datatrans/model_list.html', context, context_instance=RequestContext(request))

@staff_member_required
def model_detail(request, model, language):
    '''
    The context structure is defined as follows:

    context = {'model': '<name of model>',
               'fields': {'name': '<name of field>',
                          'items': [{'original': '<KeyValue object with original value>',
                                     'translations': [<KeyValue objects with translation>]}]
                         }
              }
    '''

    if request.method == 'POST':
        translations = [(KeyValue.objects.get(pk=int(k.split('_')[1])), v) for k, v in request.POST.items() if 'translation_' in k]
        section = [k for k, v in request.POST.items() if 'section_' in k]
        section = '#%s' % section[0] if len(section) > 0 else ''
        for keyvalue, translation in translations:
            empty = 'empty_%d' % keyvalue.pk in request.POST
            if translation != '' or empty:
                if keyvalue.value != translation:
                    keyvalue.value = translation
                keyvalue.edited = True
                keyvalue.save()
        return HttpResponseRedirect(reverse('datatrans_model_detail', args=(model, language)) + section)

    entry = _get_model_entry(model)

    default_lang = utils.get_default_language()
    model_name = u'%s' % entry[0]._meta.verbose_name
    fields = []
    first_unedited_translation = None
    for field in entry[1].fields:
        items = []
        objects = entry[0].objects.all()
        for object in objects:
            original = KeyValue.objects.get_keyvalue(object.__dict__[field], default_lang)
            translation = KeyValue.objects.get_keyvalue(object.__dict__[field], language)
            if first_unedited_translation is None and not translation.edited:
                first_unedited_translation = translation
            items.append({'original': original, 'translation': translation})
        fields.append({'name': field, 'items': items})


    context = {'model': model_name,
               'fields': fields,
               'original_language': default_lang,
               'other_language': language,
               'progress': _get_model_stats(entry[0], entry[1], lambda x: x.filter(language=language)),
               'first_unedited': first_unedited_translation}


    return render_to_response('datatrans/model_detail.html', context, context_instance=RequestContext(request))

def make_messages(request):
    utils.make_messages()
    return HttpResponseRedirect(reverse('datatrans_model_list'))
