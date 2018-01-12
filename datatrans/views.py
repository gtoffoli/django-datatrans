from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
# from django.urls import reverse
from django.template.context import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType

from datatrans import utils
from datatrans.models import KeyValue
from datatrans.utils import count_model_words

def can_translate(user):
    if not user.is_authenticated():
        return False
    elif user.is_superuser:
        return True
    else:
        group_name = getattr(settings, 'DATATRANS_GROUP_NAME', None)
        if group_name:
            from django.contrib.auth.models import Group
            translators = Group.objects.get(name=group_name)
            return translators in user.groups.all()
        else:
            return user.is_staff


def _get_model_slug(model):
    ct = ContentType.objects.get_for_model(model)
    return u'%s.%s' % (ct.app_label, ct.model)


def _get_model_entry(slug):
    app_label, model_slug = slug.split('.')
    ct = ContentType.objects.get(app_label=app_label, model=model_slug)
    model_class = ct.model_class()
    registry = utils.get_registry()
    if not model_class in registry:
        raise Http404(u'No registered model found for given query.')
    return model_class


def _get_model_stats(model, filter=lambda x: x):
    default_lang = utils.get_default_language()
    registry = utils.get_registry()
    keyvalues = filter(KeyValue.objects.for_model(model, registry[model].values()).exclude(language=default_lang))
    total = keyvalues.count()
    done = keyvalues.filter(edited=True, fuzzy=False).count()
    return (done * 100 / total if total > 0 else 0, done, total)


@user_passes_test(can_translate, settings.LOGIN_URL)
def model_list(request):
    """
    Shows an overview of models to translate, along with the fields, languages
    and progress information.
    The context structure is defined as follows:

    context = {'models': [{'languages': [('nl', 'NL', (<percent_done>, <todo>, <total>)), ('fr', 'FR', (<percent_done>, <todo>, <total>))],
                           'field_names': [u'description'],
                           'stats': (75, 15, 20),
                           'slug': u'flags_app.flag',
                           'model_name': u'flag'}]}
    """
    registry = utils.get_registry()

    default_lang = utils.get_default_language()
    languages = [l for l in settings.LANGUAGES if l[0] != default_lang]

    models = [{'slug': _get_model_slug(model),
               'model_name': u'%s' % model._meta.verbose_name,
               'field_names': [u'%s' % f.verbose_name for f in registry[model].values()],
               'stats': _get_model_stats(model),
               'words': count_model_words(model),
               'languages': [
                    (
                        l[0],
                        l[1],
                        _get_model_stats(
                            model,
                            filter=lambda x: x.filter(language=l[0])
                        ),
                    )
                    for l in languages
                ],
               } for model in registry]

    total_words = sum(m['words'] for m in models)
    context = {'models': models, 'words': total_words}

    return render(request, 'datatrans/model_list.html', context)


def commit_translations(request):
    translations = [
        (KeyValue.objects.get(pk=int(k.split('_')[1])), v)
        for k, v in request.POST.items() if 'translation_' in k]
    for keyvalue, translation in translations:
        empty = 'empty_%d' % keyvalue.pk in request.POST
        ignore = 'ignore_%d' % keyvalue.pk in request.POST
        if translation != '' or empty or ignore:
            if keyvalue.value != translation:
                if not ignore:
                    keyvalue.value = translation
                keyvalue.fuzzy = False
            if ignore:
                keyvalue.fuzzy = False
            keyvalue.edited = True
            keyvalue.save()


def get_context_object(model, fields, language, default_lang, object):
    object_item = {}
    object_item['name'] = str(object)
    object_item['id'] = object.id
    object_item['fields'] = object_fields = []
    for field in fields.values():
        key = model.objects.filter(pk=object.pk).values(field.name)[0][field.name]
        original = KeyValue.objects.get_keyvalue(key, default_lang, object, field.name)
        translation = KeyValue.objects.get_keyvalue(key, language, object, field.name)
        object_fields.append({
            'name': field.name,
            'verbose_name': str(field.verbose_name),
            'original': original,
            'translation': translation
        })
    return object_item


def needs_translation(model, fields, language, object):
    for field in fields.values():
        key = model.objects.filter(pk=object.pk).values(field.name)[0][field.name]
        translation = KeyValue.objects.get_keyvalue(key, language)
        if not translation.edited:
            return True
    return False


def editor(request, model, language, objects):
    registry = utils.get_registry()
    fields = registry[model]

    default_lang = utils.get_default_language()
    model_name = u'%s' % model._meta.verbose_name

    first_unedited_translation = None
    object_list = []
    for object in objects:
        context_object = get_context_object(
            model, fields, language, default_lang, object)
        object_list.append(context_object)

        if first_unedited_translation is None:
            for field in context_object['fields']:
                tr = field['translation']
                if not tr.edited:
                    first_unedited_translation = tr
                    break

    context = {'model': model_name,
               'objects': object_list,
               'original_language': default_lang,
               'other_language': language,
               'progress': _get_model_stats(
                   model, lambda x: x.filter(language=language)),
               'first_unedited': first_unedited_translation}

    return render(request, 'datatrans/model_detail.html', context)


def selector(request, model, language, objects):
    fields = utils.get_registry()[model]
    for object in objects:
        if needs_translation(model, fields, language, object):
            object.todo = True
    context = {
        'model': model.__name__,
        'objects': objects
    }
    return render(request, 'datatrans/object_list.html', context)

@user_passes_test(can_translate, settings.LOGIN_URL)
def object_detail(request, slug, language, object_id):
    if request.method == 'POST':
        commit_translations(request)
        return HttpResponseRedirect('.')

    model = _get_model_entry(slug)
    objects = model.objects.filter(id=int(object_id))

    return editor(request, model, language, objects)


@user_passes_test(can_translate, settings.LOGIN_URL)
def model_detail(request, slug, language):
    '''
    The context structure is defined as follows:

    context = {'model': '<name of model>',
               'objects': [{'name': '<name of object>',
                            'fields': [{
                                'name': '<name of field>',
                                'original': '<kv>',
                                'translation': '<kv>'
                            ]}],
             }
    '''

    if request.method == 'POST':
        commit_translations(request)
        return HttpResponseRedirect('.')

    model = _get_model_entry(slug)
    meta = utils.get_meta()[model]
    objects = model.objects.all()
    if getattr(meta, 'one_form_per_object', False):
        return selector(request, model, language, objects)
    else:
        return editor(request, model, language, objects)


@user_passes_test(can_translate, settings.LOGIN_URL)
def make_messages(request):
    utils.make_messages()
    return HttpResponseRedirect(reverse('datatrans_model_list'))


@user_passes_test(can_translate, settings.LOGIN_URL)
def obsolete_list(request):
    from django.db.models import Q

    default_lang = utils.get_default_language()
    all_obsoletes = utils.find_obsoletes().order_by('digest')
    obsoletes = all_obsoletes.filter(Q(edited=True) | Q(language=default_lang))

    if request.method == 'POST':
        all_obsoletes.delete()
        return HttpResponseRedirect(reverse('datatrans_obsolete_list'))

    context = {'obsoletes': obsoletes}
    return render(request, 'datatrans/obsolete_list.html', context)

from django.utils.translation import ugettext_lazy as _
from datatrans.forms import ModelTranslationForm
from datatrans.utils import REGISTRY, get_current_language
translate_map = getattr(settings, 'DATATRANS_TRANSLATE_MAP', None)
def translate(request, model, pk, app_label=''):
    languages = getattr(settings, 'LANGUAGES', [])
    if len(languages) < 2:
        raise Http404(u'No multiple languages in setting.')
    context = {}
    action_url = '/datatrans/translate/%s/%s/' % (model, pk)
    content_type = ContentType.objects.get(model=model)
    model_class = content_type.model_class()
    registry = utils.get_registry()
    if not model_class in registry:
        raise Http404(u'No registered model found for given query.')
    translatable_fields = registry[model_class]
    object = model_class.objects.get(pk=pk)
    can_translate_method = getattr(object, 'can_translate', None)
    assert not can_translate_method or object.can_translate(request)
    model_entry = translate_map[model]
    url_pattern = model_entry[0]
    url_field = model_entry[1]
    object_url = url_pattern % getattr(object, url_field)
    title_field = model_entry[2]
    object_title = getattr(object, title_field)
    edit_form_path = model_entry[3]
    components = edit_form_path.split('.')
    module = __import__(components[0])
    for component in components[1:]:
        module = getattr(module, component)
    edit_form_class = module
    edit_form = edit_form_class()
    translatable_fields = [field_name for field_name in edit_form.fields if field_name in translatable_fields]
    if request.method == 'POST':
        post_dict = request.POST
        for key, value in post_dict.items():
            if key.startswith('csrf') or key.startswith('save'):
                continue
            if key.count('_'):
                splitted = key.split('_')
                language_code = splitted[-1]
                field_name = '_'.join(splitted[:-1])
                new_value = value
                keyvalues = KeyValue.objects.filter(content_type=content_type, object_id=int(pk), field=field_name, language=language_code).order_by('-updated')
                if keyvalues:
                    keyvalue = keyvalues[0]
                    value = keyvalue.value
                    if new_value:
                        keyvalue.value = new_value
                        keyvalue.edited = True
                        keyvalue.fuzzy = False
                        keyvalue.user = request.user
                        keyvalue.save()
                        if keyvalues.count() > 1:
                            for keyvalue in keyvalues[1:]:
                                keyvalue.delete()
                    else:
                        for keyvalue in keyvalues:
                            keyvalue.delete()
                else:
                    if new_value:
                        keyvalue = KeyValue(content_type=content_type, object_id=int(pk), field=field_name, language=language_code, value=new_value, updated=True, fuzzy=False)
                        keyvalue.user = request.user
                        keyvalue.save()
            else:
                raise Http404(u'?')
    current_language = get_current_language()
    context['current_language_code'] = current_language
    context['current_language_name'] = dict(settings.LANGUAGES).get(current_language, _('unknown'))
    context['object'] = object
    original_language = object.original_language
    context['original_language'] = original_language
    context['model'] = model
    context['model_title'] = model_class._meta.verbose_name
    context['object_title'] = object_title
    context['object_url'] = object_url
    if original_language:
        form_sets = []
        for field_name in translatable_fields:
            field_forms = []
            form_field = edit_form.fields[field_name]
            for language in languages:
                initial = {}
                language_code = language[0]
                translation_field_name = '%s_%s' % (field_name, language_code)
                if language_code == original_language:
                    value = object.__dict__[field_name]
                else:
                    keyvalues = KeyValue.objects.filter(content_type=content_type, object_id=int(pk), field=field_name, language=language_code).order_by('-updated')
                    if keyvalues:
                        keyvalue = keyvalues[0]
                        value = keyvalue.value
                    else:
                        value = None
                initial[translation_field_name] = value
                field_form = ModelTranslationForm(form_field=form_field, translation_field_name=translation_field_name, initial=initial)
                field_forms.append([language_code, field_form])
            form_sets.append(field_forms)
        context['form_sets'] = form_sets
        context['action_url'] = action_url
    return render(request, 'datatrans/translate.html', context)
