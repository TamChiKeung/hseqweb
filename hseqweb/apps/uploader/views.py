import urllib
import logging

from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.conf import settings

from uploader.submissions import Submissions
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.base import View, TemplateView
from uploader.forms import UploadForm
from hseqweb.mixins import FormRequestMixin, ActionMixin
from hseqweb.virtuoso import insert
from uploader.models import Upload
from uploader.utils import api, parse_manifest_text
from uploader.utils import fix_iri_path_param
import arvados
import arvados.collection


logger = logging.getLogger(__name__)
class UploadCreateView(FormRequestMixin, CreateView):

    model = Upload
    form_class = UploadForm
    template_name = 'uploader/form.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UploadCreateView, self).get_context_data(*args, **kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self, *args, **kwargs):
        return reverse('uploader-view', kwargs={'pk': self.object.pk})


class UploadDetailView(ActionMixin, DetailView):
    model = Upload
    template_name = 'uploader/view.html'

    def get_success_url(self):
        return reverse(
            'uploader-view', kwargs={'pk': self.get_object().pk})

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_id != request.user.id:
            raise Http404
        return super(UploadDetailView, self).dispatch(request, *args, **kwargs)
    
    def on_delete(self, request, action):
        upload = self.get_object()
        if upload.status != Upload.UPLOADED:
            raise Http404
        api.collections().delete(uuid=upload.col_uuid).execute()
        upload.delete()
        return HttpResponseRedirect(reverse('uploader-list'))


class UploadListView(ListView):
    model = Upload
    template_name = 'uploader/list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        # queryset = queryset.filter(col_uuid__isnull=False)
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        else:
            queryset = queryset.filter(user__isnull=True)
        result = queryset.order_by('-date')
        for r in result:
            print(r.name, r.col_uuid)
        return result


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context

def submission_list_view(request):
    service = Submissions()

    page = request.GET.get('page') or 1
    page = int(page)

    try:
        pageSize = 20
        offset = 1
        if page > 1:
            offset = pageSize * (page - 1)

        submissions = service.find(limit=pageSize, offset=offset)
        current_page = submissions[:-1]
        num_pages = int((int(submissions[-1]['total']['value']) / pageSize)+ 1)
        has_next = True if num_pages > page else False
        has_previous = True if 1 < page else False
        next_page_number = page + 1
        previous_page_number = page - 1
        page_range = range(1,num_pages + 1)
        current_page = service.resolve_references(current_page)

    except InvalidPage as e:
        raise Http404(str(e))

    context = {
        'current_page': current_page,
        'number': page,
        'num_pages': num_pages,
        'has_next': has_next,
        'has_previous': has_previous,
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'page_range': page_range
    }
    return render(request, 'uploader/list-submission.html', context)

def submission_details_view(request, iri):
    iri = fix_iri_path_param(iri)
    service = Submissions()
    submission = service.get_by_iri(iri)
    submission = service.resolve_references([submission])[0]

    context = { 'submission': submission }

    return render(request, 'uploader/view-submission.html', context)


def collection_content(col_uuid, filename):
    c = arvados.collection.CollectionReader(col_uuid)
    with c.open(filename, "rb") as reader:
        content = reader.read(128*1024)
        while content:
            yield content
            content = reader.read(128*1024)
        
class DownloadView(View):

    def post(self, request, *args, **kwargs):
        col_uuid = self.kwargs.get('col_uuid')
        filename = self.kwargs.get('filename')
        response = StreamingHttpResponse(collection_content(col_uuid, filename))
        response['Content-Disposition'] = \
            f'attachment; filename="{filename}"'
        return response


class ValidationRunsView(TemplateView):
    template_name = 'uploader/validation_runs.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        wg_col_uuid = 'cborg-4zz18-0l7m048bpsivyzb'
        ex_col_uuid = 'cborg-4zz18-szhgxdetn190fug'
        tr_col_uuid = 'cborg-4zz18-pv7ev6qeu3d23oj'
        context['wg_col_uuid'] = wg_col_uuid
        context['ex_col_uuid'] = ex_col_uuid
        context['tr_col_uuid'] = tr_col_uuid
        col = api.collections().get(uuid=wg_col_uuid).execute()
        wg_files = parse_manifest_text(col['manifest_text'])
        context['wg_files'] = wg_files
        col = api.collections().get(uuid=ex_col_uuid).execute()
        ex_files = parse_manifest_text(col['manifest_text'])
        context['ex_files'] = ex_files
        col = api.collections().get(uuid=tr_col_uuid).execute()
        tr_files = parse_manifest_text(col['manifest_text'])
        context['tr_files'] = tr_files
        return context
