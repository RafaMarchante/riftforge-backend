import uuid
from django.db import models


class Set(models.Model):
    name = models.CharField(max_length=100, unique=True)
    set_id = models.CharField(max_length=10, unique=True)
    tcgplayer_id = models.CharField(max_length=20, blank=True, null=True)
    card_count = models.IntegerField(default=0)
    release_date = models.DateField()
    
    class Meta:
        ordering = ['release_date']
        verbose_name_plural = "Sets"
        
    def __str__(self):
        return f"{self.name} - {self.set_id}"


class Tag(models.Model):
    name = models.CharField(50)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Tags"
        
    def __str__(self):
        return self.name


class Type(models.Model):
    type = models.CharField(max_length=30)
    supertype = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        ordering = ['type', 'supertype']
        verbose_name_plural = "Types"
        unique_together = ('type', 'supertype')
        
    def __str__(self):
        return self.type if not self.supertype else f"{self.supertype} - {self.type}"

    
class Rarity(models.Model):
    name = models.CharField(max_length=20, unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Rarities"
        
    def __str__(self):
        return self.name
    
    
class Domain(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Domains"
        
    def __str__(self):
        return self.name
    
    
class Keyword(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Keywords"
        
    def __str__(self):
        return self.name


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    external_api_id = models.CharField(max_length=50, unique=True)
    riftbound_id = models.CharField(max_length=20)
    tcgplayer_id = models.CharField(max_length=20)
    might = models.IntegerField(blank=True, null=True)
    energy_cost = models.IntegerField(blank=True, null=True)
    power_cost = models.IntegerField(blank=True, null=True)
    body_text = models.TextField(default='default')
    flavour_text = models.TextField(blank=True, null=True)
    variant = models.CharField(max_length=50, blank=True, null=True)
    artist = models.CharField(max_length=50, default='default')
    image_url = models.URLField(max_length=300, default='default')
    type = models.ForeignKey(Type, on_delete=models.PROTECT, related_name='cards')
    rarity = models.ForeignKey(Rarity, on_delete=models.PROTECT, related_name='cards')
    set = models.ForeignKey(Set, on_delete=models.PROTECT, related_name='cards')
    tags = models.ManyToManyField(Tag, related_name='cards')
    domains = models.ManyToManyField(Domain, related_name='cards')
    keywords = models.ManyToManyField(Keyword, related_name='cards')
    
    class Meta:
        ordering = ['riftbound_id', 'name']
        verbose_name_plural = "Cards"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["might"]),
            models.Index(fields=["energy_cost"]),
            models.Index(fields=["power_cost"]),
            models.Index(fields=["type"]),
            models.Index(fields=["rarity"]),
            models.Index(fields=["set"]),
        ]

        
    def __str__(self):
        return f"{self.name} - {self.riftbound_id}"
