from django.db import models
from django.utils.text import slugify

class Conference(models.Model):
    conference_name = models.CharField(max_length=255, unique=True)
    conference_description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    
    def __str__(self):
        return self.conference_name
    
    def save(self, *args, **kwargs):
        if not self.slug or (self.pk and self.slug != slugify(self.conference_name)):
            self.slug = slugify(self.conference_name)
        super().save(*args, **kwargs) 

    class Meta:
        verbose_name = "Conference"
        verbose_name_plural = "Conferences"
        ordering = ['start_date']

class Track(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('conference', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.conference.conference_name})"
