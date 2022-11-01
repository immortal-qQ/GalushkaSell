import os

from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import *
from .models import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TgUserViewSet(viewsets.ModelViewSet):
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer

    @action(detail=True, methods=['post'])
    def update_vk_link(self, request, pk=None):
        tg_user = self.get_object()
        serializer = TgUserSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            tg_user.vk_link = serializer.validated_data['vk_link']
            tg_user.save()
            return Response({'success': 'True', 'changes': {'vk_link': tg_user.vk_link}})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def update_state(self, request, pk=None):
        tg_user = self.get_object()

        # takes field required to verif admin and prepares data for serializer
        try:
            requested_by = TgUser.objects.get(tg_id=request.data.get('requested_by'))
        except Exception as e:
            print(e)
            return Response({'error': 'requested_by user not found'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TgUserSerializer(data=request.data, partial=True)

        if serializer.is_valid():

            # discards req if admin tried to edit admin
            if requested_by.role == 'A' and tg_user.role == 'A':
                return Response({'error': 'Admins not allowed to edit admins'}, status=status.HTTP_400_BAD_REQUEST)

            # discards req if requested not by admin
            if requested_by.role != 'A':
                return Response({'error': 'Only for admins allowed'}, status=status.HTTP_400_BAD_REQUEST)

            tg_user.state = serializer.validated_data['state']
            tg_user.save()
            return Response({'success': 'True', 'changes': {'user': tg_user.tg_id, 'state': tg_user.state}})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def update_role(self, request, pk=None):
        tg_user = self.get_object()
        serializer = TgUserSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            tg_user.role = serializer.validated_data['role']
            tg_user.save()
            return Response({'success': 'True', 'changes': {'user': tg_user.tg_id, 'role': tg_user.role}})
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=True)
    def favourite(self, request, pk=None):
        tg_user = self.get_object()
        serializer = FavouriteRecordSerializer(FavouriteRecord.objects.filter(user=tg_user), many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def add_favourite(self, request, pk=None):
        tg_user = self.get_object()
        existed = None
        try:
            existed = FavouriteRecord.objects.get(user=tg_user, post=Post.objects.get(pk=request.data['add']))
        except Exception as e:
            pass
        try:
            if existed is None:
                FavouriteRecord(user=tg_user, post=Post.objects.get(pk=request.data['add'])).save()
                return Response({'success': 'True'})
            else:
                return Response("Already exists", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def remove_favourite(self, request, pk=None):
        tg_user = self.get_object()
        try:
            FavouriteRecord.objects.get(user=tg_user, post=Post.objects.get(pk=request.data['remove'])).delete()
            return Response({'success': 'True'})
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(author__state='A')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'category', 'status']

    @action(detail=True, methods=['post'])
    def update_header(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            post.header = serializer.validated_data['header']
            post.save()
            return Response({'success': 'True', 'changes': {'header': post.header}})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            post = self.get_object()
            os.remove(os.path.join(os.getcwd(), 'media', str(post.image)))
            self.perform_destroy(post)
            return Response({'success': 'True'})
        except Exception as e:
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            post.price = int(serializer.validated_data['price'])
            post.save()
            return Response({'success': 'True', 'changes': {'price': str(post.price)}})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            post.status = serializer.validated_data['status']
            post.save()
            return Response({'success': 'True', 'changes': {'status': post.status}})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_image(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            prev_file = post.image
            post.image = request.FILES['image']
            post.save()
            os.remove(os.path.join(os.getcwd(), 'media', str(prev_file)))
            return Response({'success': 'True', 'changes': {'image': str(post.image)}})
        else:
            return Response({'error': 'unknown'})

    @action(detail=True, methods=['post'])
    def update_description(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            post.description = serializer.validated_data['description']
            post.save()
            return Response({'success': 'True', 'changes': {'description': post.description}})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def favourite_by(self, request, pk=None):
        post = self.get_object()
        serializer = FavouriteRecordSerializer(FavouriteRecord.objects.filter(post=post), many=True)
        return Response(serializer.data)


class FavouriteRecordViewSet(viewsets.ModelViewSet):
    queryset = FavouriteRecord.objects.all()
    serializer_class = FavouriteRecordSerializer
