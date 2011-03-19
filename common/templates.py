from django.template import Context, loader
from django.core.context_processors import csrf

def render_template(name, request, dict_):
    template = loader.get_template(name)
    dict_.update({'authenticated': request.user.is_authenticated(),
                  'name': request.user.username})
    dict_.update(csrf(request))
    context = Context(dict_)
    return template.render(context)
