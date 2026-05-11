from django.contrib import admin
from .models import RDVScoreLog, RecommendationLog, EventLog

admin.site.register(RDVScoreLog)
admin.site.register(RecommendationLog)
admin.site.register(EventLog)
