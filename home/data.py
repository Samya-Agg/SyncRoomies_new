from .models import student
from django.shortcuts import render,HttpResponse,request

def get_data(n):
    for i in range(0,10):
        if request.method=="POST":
          data=request.POST

          sleep=data.get('sleep')
          if (sleep=='intro'):
             sleep=1
          else:
             sleep=0
          type=data.get('type')
          nature=data.get('nature')

          student.objects.create(
            sleep=sleep,
            type=type,
            nature=nature
        )

          return render(request,'student.html')
