from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import RegistrationForm


@login_required
def index(request):
    return render(request, 'exam/index.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(
                form.cleaned_data['password']
            )
            new_user.save()
            return render(request,
                          'registration/register_done.html',
                          {'new_user': new_user})
    else:
        form = RegistrationForm()
    return render(request,
                  'registration/register.html',
                  {'form': form})


def test(request):
    return render(request, 'test.html')
