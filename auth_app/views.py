from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import UserProfile
from django.core.mail import send_mail
from .tokens import EmailConfirmationTokenGenerator
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import reverse


# Vue pour gérer la connexion des utilisateurs
def login_view(request: WSGIRequest):
    if request.method == 'POST':
        # get username and password from WSGIRequest object
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')

        # get the User object if authentification is ok, None otherwise
        user: User = authenticate(request, username=username, password=password)
        if user is not None:
            print(username, password, user, " ok ! ")
            login(request, user)
            return redirect('home')
        print("personne dans la db")
        messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    print("redirection vers auth_app/login.html")
    return render(request, 'auth_app/login.html')


# Vue pour gérer la déconnexion des utilisateurs
def logout_view(request):
    print("enter logout")
    logout(request)
    print("logout request done")
    return redirect('home')


# Vue pour gérer l'enregistrement des utilisateurs
def register_view(request: WSGIRequest):
    print("enter register ", str(WSGIRequest))
    if request.method == "POST":
        print("POST")
        form: UserRegistrationForm = UserRegistrationForm(request.POST)
        if form.is_valid():
            print("form valid")
            user: User = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            print("login done")
            email_confirmation_token: EmailConfirmationTokenGenerator = EmailConfirmationTokenGenerator()
            print("email_token: ", email_confirmation_token)
            token: str = email_confirmation_token.make_token(user)
            print("token = ", token)
            confirmation_link = request.build_absolute_uri(reverse('auth_app:confirm', args=[token]))
            send_mail(
                'Email confirmation',
                'Please confirm your email by clicking on the following link: ' + str(confirmation_link),
                'admin-corankco@mailo.com',
                [user.email],
                fail_silently=False,
            )
            print("email sent")
            messages.success(request, "Registration successful.")
            print("redirect home")
            return redirect('home')
        print("form not valid")
        print(form.errors)  # Ajoutez cette ligne
        messages.error(request, "Unsuccessful registration. Invalid information.")
    print("Pas de POST")
    form: UserRegistrationForm = UserRegistrationForm()
    print("render, request = ", request, " template = auth_app/register.html")
    return render(request=request, template_name="auth_app/register.html", context={"register_form": form})


@login_required
def profile_view(request, username):
    if request.user.username == username:
        user = get_object_or_404(User, email=username)
        context = {
            "user": user,
        }
        return render(request, 'auth_app/profile.html', context)
    else:
        raise Http404


def confirm_view(request, token):
    email_confirmation_token = EmailConfirmationTokenGenerator()
    for user in User.objects.all():
        print(user.email)
        if email_confirmation_token.check_token(user, token):
            # Update user profile
            print("enter with email", user.email)
            profile = UserProfile.objects.get(user=user)
            print("get profile ", print(profile.user))
            profile.email_verified = True
            profile.save()
            print("save done")
            messages.success(request, "Email confirmed successfully.")
            return render(request, "auth_app/confirmation.html", {
                'message': 'Thanks for verifying your email address, you can now fully use corankco website'})

    messages.error(request, "Invalid confirmation link.")
    return HttpResponse('Invalid confirmation link')
