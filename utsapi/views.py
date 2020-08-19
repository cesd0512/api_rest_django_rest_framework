from django.shortcuts import render
from rest_framework import viewsets
from django.core.files.storage import FileSystemStorage
from .serializers import FileSerializer
from .models import File
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
# from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.http import FileResponse


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all().order_by('id')
    serializer_class = FileSerializer

    def create(self, request):
        id_download = request.data.get('download', None)
        if id_download:
            return self._download(id_download)
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name_ = fs.save(uploaded_file.name, uploaded_file)
        route_ = fs.url(name_)
        ext_ = name_.split('.')
        ext_ = ext_[1] if ext_ else None
        obj = File(name=name_, extension=ext_, route=route_)
        obj.save()
        return Response({
            'status': 'File created', 
            'object': {
            'id': obj.id,
            'name': obj.name,
            'extension': obj.extension
        }})
    
    def retrieve(self, request, pk=None):
        if pk:
            return self._download(pk)
        return Response({'status': 'Operation not permited'})

    
    # def get_queryset(self):
    #     queryset = File.objects.all()
    #     id_download = self.request.query_params.get('download', None)
    #     if id_download:
    #         return self._download(id_download)
    #     return queryset

    def _download(self, pk):
        response = Response({'status': 'error'})
        obj = File.objects.get(id=pk)
        if obj:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.name)
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'))
        return response

    # def list(self, request):
    #     return Response({'status': 'Operation not permited'})

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass

    # def get_queryset(self):
    #     queryset = File.objects.all()
        # estudiante = self.request.query_params.get('name', None)
        # grupo = self.request.query_params.get('grupo', None)
        # nota = self.request.query_params.get('nota', None)
        # if estudiante is not None:
        #     queryset = Notas.objects.filter(estudiante__icontains=estudiante)
        # elif grupo is not None:
        #     queryset = Notas.objects.filter(grupo__icontains=grupo)
        # elif nota is not None:
        #     queryset = Notas.objects.filter(nota__icontains=nota)
        # return queryset

# def download_file(request, pk):
#     print(pk)
#     if request.method == 'POST':
#         obj = File.objects.get(id=pk)
#         print(obj)
#         if obj:
#             file_path = os.path.join(settings.MEDIA_ROOT, obj.name)
#             if os.path.exists(file_path):
#                 with open(file_path, 'rb') as fh:
#                     response = HttpResponse(fh.read())
#                     response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
#                     return response
#     else:
#         return JsonResponse({'error': 'Error!!! method not accepted'}, status=401)
#     raise Http404
