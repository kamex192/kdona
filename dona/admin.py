from django.contrib import admin

from .models import Rakuten_books
from .models import Yahoo
from .models import Mono
from .models import Gei
from .models import Antlion

admin.site.register(Rakuten_books)
admin.site.register(Yahoo)
admin.site.register(Gei)
admin.site.register(Mono)
admin.site.register(Antlion)
