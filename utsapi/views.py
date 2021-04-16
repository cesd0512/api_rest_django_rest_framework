import os
import sys
from datetime import datetime, date
import json
import calendar

#Django
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.http import FileResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.utils import timezone
import rest_framework.status as STATUS
from django.forms.models import model_to_dict

# from django.shortcuts import redirect
# from django.urls import reverse_lazy

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.settings import api_settings

#Models and Serializers
from .serializers import FileSerializer, ProjectSerializer, UserEditSerializer, ProfileEditSerializer
from .models import File, Project, FileDownload, Profile
from .send_email import send_email


from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


URL_SERVER = os.getenv('BASE_URL_SERVER')
                             

def file_download_res(obj):
    file_path = os.path.join(obj.media.path)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    return response
    # return redirect('http://localhost:8000/media/message/2021/01/07/297124024004.pdf?var=2')


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
            subject = "Recover password | Cloud4files"
            user_, = User.objects.filter(email=email)
            if not user_:
                return Response({'status': 'error', 'message': 'Account not found'}, status=STATUS.HTTP_400_BAD_REQUEST)
            url_ = URL_SERVER + 'password-reset/?u=' + str(user_.id)
            send_email(subject, url_, email, user_.username)
            return Response({'status': 'ok', 'message': 'sended mail successful!'}, status=STATUS.HTTP_200_OK)

        user_id = request.data.get('user', None)
        n_pass = request.data.get('password', None)
        if not n_pass:
            return Response({'status': 'error', 'message': 'Empty arguments!'})
        user, = User.objects.filter(id=int(user_id))
        if user is not None:
            user.set_password(n_pass)
            user.save()
            return Response({'status': 'ok', 'message': 'Password changed'}, status=STATUS.HTTP_200_OK)
        else:
            return Response({'status': 'error', 'message': 'Error user not found'}, status=STATUS.HTTP_400_BAD_REQUEST)


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
        

class UpdateUser(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request):
        user_object = request.data.get('user', None)
        user_object = json.loads(user_object)
        user = request.user
        profile = Profile.objects.get(user_id=user.id)
        try:
            photo = request.FILES['photo']
            profile.photo = photo
            profile.save()
        except Exception as e:
            print('error'*200)
            print(e)
        # if 1:
        try:
            serializer_ = UserEditSerializer(user, data=user_object)
            if serializer_.is_valid():
                instance = serializer_.save()
                serializer_ = ProfileEditSerializer(profile, data=user_object)
                if serializer_.is_valid():
                    instance_prof = serializer_.save()
                else:
                    print('Error guardar profile', serializer_.errors)        
                token, _ = Token.objects.get_or_create(user=user)
                user_dict = model_to_dict(user)
                profile_dict = model_to_dict(profile)
                user_dict.update(profile_dict)
                user_dict['token'] = token.key
                user_dict['photo'] = ''
                user_dict['photo_url'] = profile.photo.url if profile.photo else ''
                return Response({'user': user_dict, 'message': 'User updated'})
            else:
                print('Error guardar user', serializer_.errors)
            return Response({"error": serializer_.errors}, status=STATUS.HTTP_400_BAD_REQUEST)
        except Exception as inst:
            print(inst.args)
            return Response({'detail': inst.args}, status=STATUS.HTTP_400_BAD_REQUEST)
        

class UpdateSecurityAccount(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        password = request.data.get('password', '')
        email = request.data.get('email', '')
        alternative_email = request.data.get('alternative_email', '')
        user = request.user
        
        try:
            if password:
                user.set_password(password)
            if email:
                user.email = email
            user.save()
            
            profile = Profile.objects.get(user_id=user.id)
            if alternative_email:
                profile.alternative_email = alternative_email
            profile.save()
            
            return Response({'status': 'ok'}, status=STATUS.HTTP_200_OK)
        except Exception as e:
            return Response({"status": 'error', 'msg': str(e)}, status=STATUS.HTTP_400_BAD_REQUEST)


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
            user = User.objects.create_user(username=name, password=password, first_name=fname, 
                        last_name=lname, email=email)
            user.save()
            profile = Profile(user=user)
            profile.save()
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
            profile = Profile.objects.get(user_id=user.id)
            last_login = timezone.localtime(user.last_login, timezone.get_fixed_timezone(-300))
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            user_res = {
                'username': user.username,
                'email': user.email,
                'last_login': last_login,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': profile.phone,
                'country': profile.country,
                'city': profile.city,
                'birthday': profile.birthday,
                'profession': profile.profession,
                'photo': profile.photo.url if profile.photo else '',
                'photo_url': profile.photo.url if profile.photo else '',
                'alternative_email': profile.alternative_email,
                'token': token.key
            }
            return Response({'valid': True, 'user': user_res})
        else:
            return Response({'valid': False, 'user': {}})


class DownloadFile(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        if not pk:
            return {
                'result': 'error', 
                'message': 'Key file is required'
                }
        response = Response({'status': 'Key not found'})
        file_, = File.objects.filter(id=int(pk))
        if file_:
            now = datetime.now()
            file_.download_date = now
            file_.save()
            file_download = FileDownload(file=file_, download_date=now)
            file_download.save()
            return file_download_res(file_)
        return response
    

class MonthsIndicatorsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        # months = request.data.get('months', [])
        months_dict = {}
        current_month = date.today().month
        _month = current_month
        months = ["", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        for i in range(6):
            _year = date.today().year
            if _month == 0:
                _month = 12
            if _month > current_month:
                _year -= 1 
            _last_day_month = calendar.monthrange(_year, _month)
            first_date = date(_year, _month, 1)
            last_date = date(_year, _month, _last_day_month[1])
            qty_down = FileDownload.objects.filter(
                file__owner_id=user_id,
                download_date__gte=first_date,
                download_date__lte=last_date
                ).count()
            months_dict[months[_month]] = qty_down
            _month -= 1
            
        return Response(months_dict, status=STATUS.HTTP_200_OK)


class TotalsIndicatorsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        files = File.objects.filter(owner_id=user_id).count()
        downloads = FileDownload.objects.filter(file__owner_id=user_id).count()
        projects = Project.objects.filter(owner_id=user_id).count()
        data = {
            'files': files,
            'downloads': downloads,
            'projects': projects,
        }
        print(data)
        return Response(data, status=STATUS.HTTP_200_OK)


class FavoriteFiles(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        fav = request.data.get('favorite', False)
        files = File.objects.filter(favorite=True, owner_id=user_id)
        data = []
        for file in files:
            data.append({
                'id': file.id,
                'name': file.name,
                'extension': file.extension,
                'project': file.project.name,
                'created_at': file.created_at,
                'updated_at': file.updated_at,
                'media': file.media.url
            })
        
        return Response(data, status=STATUS.HTTP_200_OK)


class UpdateFavoriteFiles(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk=None):
        user_id = request.user.id
        fav = request.data.get('favorite', False)
        file, = File.objects.filter(id=pk)
        if file.owner.id != user_id:
            return Response({'status': 'Operation not permited'})
        file.favorite = fav
        file.save()
        return Response({
                    'id': file.id,
                    'name': file.name.replace('.' + file.extension, ''),
                    'extension': file.extension,
                    'route': file.route,
                    'favorite': file.favorite,
                    'created_date': file.created_at,
                    'project': file.project.name,
                    'url': file.media.url
                })


class FilesFromProject(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer
    pagination_class = PageNumberPagination

    def post(self, request, format=None):
        """
        Return file list of project.
        """
        user_id = request.user.id
        project_id = request.data.get('project', None)
        pagination = request.data.get('pagination', None)
        search = request.data.get('search', None)
        if search:
            files = File.objects.filter(
                owner=user_id, project=project_id, name__icontains=search
                ).order_by('name')
        else:
            files = File.objects.filter(owner=user_id, project=project_id).order_by('name')

        if pagination:
            if not isinstance(pagination, int):
                return Response({'message': 'Pagination parameter must be integer'})
            self.pagination_class.page_size = int(pagination)
            page = self.paginate_queryset(files)
            if page is not None:
                factory = APIRequestFactory()
                request = factory.get('/')
                serializer_context = {
                    'request': Request(request),
                }
                serializer = self.serializer_class(page, many=True, context=serializer_context)
                return self.get_paginated_response(serializer.data)
        else:
            list_obj = []
            for f in files:
                list_obj.append({
                    'id': f.id,
                    'name': f.name.replace('.' + f.extension, ''),
                    'extension': f.extension,
                    'route': f.route,
                    'favorite': f.favorite,
                    'created_date': f.created_at,
                    'project': f.project.name,
                    'url': f.media.url
                })
            return Response({'results': list_obj})
    
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data) 


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('id')
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)  
    
    def get_queryset(self):
        queryset = Project.objects.all()
        user = self.request.user.id
        if user is not None:
            queryset = Project.objects.filter(owner=user).order_by('name')
        return queryset

    def create(self, request):
        user = request.user
        name = request.data.get('name', None)
        description = request.data.get('description', None)
        obj = Project(name=name, owner=user, description=description)
        obj.save()
        return Response({
            'status': 'Project created', 
            'project': {
                'id': obj.id,
                'name': obj.name,
                'description': obj.description,
                'updated_at': obj.updated_at
            }
        })
        
    def update(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        if not project:
            return Response({'message': 'Project not found'})
        user_id = request.user.id
        if project.owner.id != user_id:
            return Response({'status': 'Operation not permited'})
        super(ProjectViewSet, self).update(request, pk)
        return Response(Project.objects.filter(owner_id=user_id).values())


class RecentProjects(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Return recent projects consulted.
        """
        user = request.user
        projects = Project.objects.filter(owner=user).exclude(consulted_date=None).values(
            'id', 'name', 'description', 'updated_at', 'consulted_date').order_by('-consulted_date')[:5] 
        return Response(list(projects))

    def post(self, request):
        user = request.user
        project_id = request.data.get('project', None)
        project, = Project.objects.filter(id=project_id)
        project.consulted_date = datetime.now()
        project.save()
        return Response({'result': 'ok'})


class RecentDownloadFiles(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Return recent download files.
        """
        user = request.user
        projects = File.objects.filter(owner=user).exclude(download_date=None).values(
            'id', 'name', 'favorite', 'project', 'updated_at', 'extension',  'download_date').order_by(
            '-download_date')[:8] 
        return Response(list(projects))


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all().order_by('id')
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    page_size = 8
    
    def get_queryset(self):
        user_id = self.request.user.id
        pagination = self.request.query_params.get('pagination', None)
        search = self.request.query_params.get('search', None)
        if (pagination):
            self.pagination_class.page_size = int(pagination)
        
        if search:
            queryset = File.objects.filter(
                owner=user_id, name__icontains=search
                ).order_by('name')
        else:
            queryset = File.objects.filter(owner=user_id).order_by('name')
            
        return queryset

    def create(self, request):
        uploaded_file = request.FILES['document']
        # fs = FileSystemStorage()
        # name_ = fs.save(uploaded_file.name, uploaded_file)
        # route_ = fs.url(name_)
        name_ = uploaded_file.name
        ext_ = name_.split('.')
        ext_ = ext_[-1] if ext_ else None
        project_id = request.data.get('project', None)
        project = None
        if project_id:
            project = Project.objects.get(id=project_id)
        user = request.user
        obj = File(name=name_, extension=ext_, project=project, owner=user, media=uploaded_file)
        obj.save()
        return Response({
            'status': 'File created', 
            'object': {
                'id': obj.id,
                'name': obj.name,
                'extension': obj.extension,
                'route': obj.route,
                'favorite': obj.favorite,
                'created_date': obj.created_at,
                'project': obj.project.name if obj.project else '',
                'url': obj.media.url
                }
            })
    
    def retrieve(self, request, pk=None):
        file_, = File.objects.filter(id=pk)

        print(file_.media.storage.get_accessed_time(file_.media.name))

        if not file_:
            return Response({'message': 'File not exist'})
        user_id = self.request.user.id
        if file_.owner.id != user_id:
            return Response({'status': 'Operation not permited'})
        # return self.file_download_res(pk)
        return super(FileViewSet, self).retrieve(request, pk)

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass
