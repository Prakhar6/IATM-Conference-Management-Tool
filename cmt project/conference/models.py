from django.db import models
from django.utils.text import slugify

class Conference(models.Model):
    conference_name = models.CharField(max_length=200)
    conference_description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.conference_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.conference_name

    class Meta:
        verbose_name = "Conference"
        verbose_name_plural = "Conferences"
        ordering = ['start_date']

class Track(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=200)
    
    class Meta:
        unique_together = ('conference', 'name')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.conference.conference_name})"
