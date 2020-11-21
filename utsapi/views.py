from django.shortcuts import render
from rest_framework import viewsets
from django.core.files.storage import FileSystemStorage
from .serializers import FileSerializer, ProjectSerializer
from .models import File, Project
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
import sys
from django.http import JsonResponse
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, Http404, HttpResponseServerError
from .send_email import send_email
from django.urls import reverse_lazy


class CurrentUser(APIView):
    permission_classes = (IsAuthenticated,)  

    def get(self, request, format=None):
        """
        Return current user.
        """
        user = request.user
        user_res = {
            'username': user.username,
            'email': user.email,
            'last_login': user.last_login,
            'first_name': user.first_name,
            'last_name': user.last_name
            }
        return Response(user_res)


class RecoveryPassword(APIView):

    def post(self, request, format=None):
        """
        Return state of change password.
        """
        email = request.data.get('email', None)
        if email:
            subject = "Reset password"
            user_, = User.objects.filter(email=email)
            base_url = 'http://localhost:8080/password-reset/?u=' + str(user_.id)
            message = "Hello! \n To recover your password enter the following link: \n \n" + base_url
            send_email(subject, message, email)
            return Response({'status': 'ok', 'message': 'sended mail successful!'})

        user_id = request.data.get('user', None)
        n_pass = request.data.get('password', None)
        if not n_pass:
            return Response({'status': 'error', 'message': 'Empty arguments!'})
        user, = User.objects.filter(id=int(user_id))
        if user is not None:
            user.set_password(n_pass)
            user.save()
            return Response({'status': 'ok', 'message': 'Password changed'})
        else:
            return Response({'status': 'error', 'message': 'Error user not found'})


class ChangePassword(APIView):
    permission_classes = (IsAuthenticated,) 

    def post(self, request, format=None):
        """
        Return state of change password.
        """
        user = request.user
        c_pass = request.data.get('current_password', None)
        n_pass = request.data.get('new_password', None)
        if not c_pass or not n_pass:
            return Response({'status': 'error', 'message': 'Empty arguments!'})
        auth_ = authenticate(username=user.username, password=c_pass)
        if auth_ is not None:
            user.set_password(n_pass)
            user.save()
            return Response({'status': 'ok', 'message': 'Password changed'})
        else:
            return Response({'status': 'error', 'message': 'Error in current password'})


class CreateUser(APIView):

    def post(self, request, format=None):
        password = request.data.get('password', None)
        name = request.data.get('username', None)
        fname = request.data.get('first_name', None)
        lname = request.data.get('last_name', None)
        email = request.data.get('email', None)
        if not password or not name or not fname or not lname or not email:
            return Response({'status': 'error', 'message': 'Empty arguments!'})
        try:
            user = User.objects.create_user(username=name, password=password, first_name=fname, last_name=lname, email=email)
            user.save()
        except Exception as inst:
            return Response({'detail': inst.args})
        return Response({'status': 'ok', 'message': 'User created successful'})



class LogoutUser(APIView):
    permission_classes = (IsAuthenticated,)  

    def post(self, request, format=None):
        logout(request)
        return Response({'status': 'ok', 'message': 'Logout successful!'})


class AuthenticateUser(APIView):

    def post(self, request, format=None):
        """
        Return valid authentication.
        """
        name = request.data.get('username', None)
        password = request.data.get('password', None)
        user = authenticate(username=name, password=password)
        if user is not None:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            user_res = {
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key,
            }
            return Response({'valid': True, 'user': user_res})
        else:
            return Response({'valid': False, 'user': {}})


class FilesFromProject(APIView):
    permission_classes = (IsAuthenticated,) 

    def post(self, request, format=None):
        """
        Return file list of project.
        """
        user_id = request.user.id
        project_id = request.data.get('project', None)
        files = File.objects.filter(owner=user_id, project=project_id)
        list_obj = []
        for f in files:
            list_obj.append({
                'name': f.name,
                'extension': f.extension,
                'route': f.route,
                'favorite': f.favorite,
                'created_date': f.created_at,
                'project': f.project.name,
            })

        return Response(list_obj)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('id')
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)  

    def create(self, request):
        user = request.user
        name = request.data.get('name', None)
        description = request.data.get('description', None)
        obj = Project(name=name, owner=user, description=description)
        obj.save()
        return Response({
            'status': 'Project created', 
            'object': {
            'id': obj.id,
            'name': obj.name
            }
        })
    
    def get_queryset(self):
        queryset = Project.objects.all()
        user = self.request.user.id
        if user is not None:
            queryset = Project.objects.filter(owner=user)
        return queryset


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all().order_by('id')
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated,)  

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
        project = request.data.get('project', None)
        obj_project = Project.objects.get(id=project)
        user = request.user
        obj = File(name=name_, extension=ext_, route=route_, project=obj_project, owner=user)
        obj.save()
        return Response({
            'status': 'File created', 
            'object': {
            'id': obj.id,
            'name': obj.name,
            'extension': obj.extension
        }})
    
    def retrieve(self, request, pk=None):
        file_ = File.objects.filter(id=pk)
        if not file_:
            return Response({'message': 'File not exist'})
        user_id = self.request.user.id
        if file_[0].owner.id != user_id:
            return Response({'status': 'Operation not permited'})
        return self._download(pk)
        # return super(FileViewSet, self).retrieve(request, pk)

    def get_queryset(self):
        queryset = File.objects.all()
        user = self.request.user.id
        if user is not None:
            queryset = File.objects.filter(owner=user)
        return queryset

    def _download(self, pk):
        response = Response({'status': 'error'})
        obj = File.objects.get(id=pk)
        if obj:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.name)
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'))
        return response

    # def get_queryset(self):
    #     queryset = File.objects.all()
    #     id_download = self.request.query_params.get('download', None)
    #     if id_download:
    #         return self._download(id_download)
    #     return queryset

    # def list(self, request):
    #     return Response({'status': 'Operation not permited'})

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass

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
