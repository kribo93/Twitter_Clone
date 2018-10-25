from django.contrib import admin
from .models import Tweet, TweetMedia
from .forms import TweetModelForm

# Register your models here.

class TweetMediaInline(admin.TabularInline):
    model = TweetMedia

class TweetModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'user',)
    inlines = [TweetMediaInline]

admin.site.register(Tweet, TweetModelAdmin)
admin.site.register(TweetMedia)

