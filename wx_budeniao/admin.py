from django.contrib import admin

from .models import user  # 导入自定义表格的类

# Register your models here.
admin.site.register(user)  # 登记该表格，便于在后台显示
