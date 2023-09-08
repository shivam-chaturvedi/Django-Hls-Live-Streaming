from django.shortcuts import render

# path  : '/' for recoding of live stream
def home(req):
    res=render(req,'index.html')
    return res

# path :'/viewers' for viewing live streaming 
def viewers(req):
    res= render(req,'viewers.html')
    return res
