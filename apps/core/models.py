from django.db import models


class Skill(models.Model):
    name = models.CharField('nom', max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'compétence'
        verbose_name_plural = 'compétences'