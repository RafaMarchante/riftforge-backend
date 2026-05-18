import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Deck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Decks'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_public']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class DeckCard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='deck_cards')
    card = models.ForeignKey('cards.Card', on_delete=models.PROTECT, related_name='in_decks')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('deck', 'card')
        verbose_name_plural = 'Deck Cards'

    def __str__(self):
        return f"{self.deck.name} - {self.card.name} x{self.quantity}"


class DeckLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_decks')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'deck')
        verbose_name_plural = 'Deck Likes'

    def __str__(self):
        return f"{self.user.username} liked {self.deck.name}"


class DeckView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_decks')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='views')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'deck')
        verbose_name_plural = 'Deck Views'

    def __str__(self):
        return f"{self.user.username} viewed {self.deck.name}"
