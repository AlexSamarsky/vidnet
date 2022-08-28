# from datetime import datetime
from django.db import models

from django.utils import timezone

from users.models import User


REACTIONS = [
    ('HRT', 'Лайк'),
    ('FG', 'Большой палец'),
    ('SM', 'Улыбка'),
]


def user_directory_path(instance, filename):

    return 'author_{0}/{1}'.format(instance.author.id, filename)


class Category(models.Model):
    name = models.CharField(verbose_name="Наименование",
                            blank=False, max_length=40)

    def __str__(self) -> str:
        return self.name


class Reaction(models.Model):
    name = models.CharField(verbose_name="Наименование",
                            blank=False, max_length=40)
    icon = models.CharField(verbose_name="Иконка",
                            blank=False, choices=REACTIONS, max_length=40)

    def __str__(self) -> str:
        return self.name


class Videoclip(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(verbose_name="Название",
                             blank=False, max_length=100)
    description = models.TextField(verbose_name="Описание", blank=False)
    upload = models.FileField(upload_to=user_directory_path, blank=True)
    categories = models.ManyToManyField(
        Category, through="VCCategory", verbose_name="Категории")
    create_date = models.DateTimeField(
        verbose_name="Дата создания", default=timezone.now)

    def __str__(self) -> str:
        return f"{self.title}, Автор: {self.author}"


class VCComment(models.Model):
    videoclip = models.ForeignKey(
        Videoclip, on_delete=models.CASCADE, verbose_name="Видео")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    create_date = models.DateTimeField(
        verbose_name="Дата", default=timezone.now)
    comment = models.TextField(verbose_name="Комментарий")

    def __str__(self) -> str:
        return f"{str(self.user)} / {self.create_date}"


class VCReaction(models.Model):
    videoclip = models.ForeignKey(
        Videoclip, on_delete=models.CASCADE, verbose_name="Видео",
        related_name='reactions')
    reaction = models.ForeignKey(
        Reaction, on_delete=models.CASCADE, verbose_name="Реакция")
    count = models.IntegerField(verbose_name="Количество", default=0)


class UserReaction(models.Model):
    videoclip = models.ForeignKey(
        Videoclip, on_delete=models.CASCADE, verbose_name="Видео")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    reaction = models.ForeignKey(
        Reaction, on_delete=models.CASCADE, verbose_name="Реакция")
    create_date = models.DateTimeField(
        verbose_name="Дата", default=timezone.now)

    class Meta:
        unique_together = ('videoclip', 'user', 'reaction')

    def register_reaction(self):
        vc_reaction = VCReaction.objects.get_or_create(
            videoclip=self.videoclip, reaction=self.reaction)
        vc_reaction_object = vc_reaction[0]
        if not vc_reaction_object.count:
            vc_reaction_object.count = 0
        vc_reaction_object.count += 1
        vc_reaction_object.save()

    def unregister_reaction(self):
        vc_reaction = VCReaction.objects.get(
            videoclip=self.videoclip, reaction=self.reaction)
        vc_reaction.count -= 1
        vc_reaction.save()


class VCSubscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория")
    create_date = models.DateTimeField(
        verbose_name="Дата", default=timezone.now)

    class Meta:
        unique_together = ('user', 'category')


class VCBan(models.Model):
    videoclip = models.ForeignKey(
        Videoclip, on_delete=models.CASCADE, verbose_name="Видео")
    banned_user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    term_date = models.DateTimeField(verbose_name="Бан до")
    create_date = models.DateTimeField(
        verbose_name="Дата", default=timezone.now)

    class Meta:
        unique_together = ('videoclip', 'banned_user')


class VCCategory(models.Model):
    videoclip = models.ForeignKey(
        Videoclip, on_delete=models.CASCADE, verbose_name="Видео")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория")

    def __str__(self) -> str:
        return f"{str(self.videoclip)} / {str(self.category)}"
