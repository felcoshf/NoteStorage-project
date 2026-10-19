from django.shortcuts import render

def unathorize_page(request):
    return render(request, 'index/home.html')

#представления джанго связаные со входом