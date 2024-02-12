from django.contrib import admin
from .models import (
    TotalByDay,
    Video,
    Report,
    GenderDistribution,
    Territory,
    TotalFollowers,
    FollowersActivity,
)


admin.site.register(FollowersActivity)
admin.site.register(TotalByDay)
admin.site.register(Video)
admin.site.register(Report)
admin.site.register(GenderDistribution)
admin.site.register(Territory)
admin.site.register(TotalFollowers)

# Register your models here.
