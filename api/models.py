from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class TgUser(models.Model):
    tg_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    nickname = models.CharField(max_length=100, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    vk_link = models.URLField(default='https://vk.com')
    role = models.CharField(max_length=1, default='U', choices=[
        ('U', 'User'),
        ('A', 'Admin')
    ])
    state = models.CharField(max_length=1, choices=[
        ('A', 'Active'),
        ('B', 'Blocked')
    ], default='A')

    def __str__(self):
        return f"Nickname: {self.nickname}. TelegramId: {self.tg_id}"


class Category(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='Категория')
    name = models.CharField(max_length=50,)
    emoji_id = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        try:
            return f"{self.name}, Родитель: {Category.objects.get(pk=self.parent_id).name} [id = {self.parent.id}]"
        except Category.DoesNotExist:
            return str(self.name)


class Post(models.Model):
    author = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    header = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    image = models.ImageField(upload_to=f'media/post_images')
    # Active - shown in pool of posts; Stopped - hidden from main pool of posts, may be called with special req
    status = models.CharField(max_length=1, choices=[
        ('A', 'Active'),
        ('S', 'Stopped'),
    ], default='A')

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        try:
            author = TgUser.objects.get(pk=self.author.tg_id).nickname
        except TgUser.DoesNotExist:
            author = None
        finally:
            return f"Post: {self.header}. By: {author}"


class FavouriteRecord(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
