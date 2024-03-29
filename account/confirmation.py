from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import  urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.views.generic import TemplateView
from django.core.exceptions import  ValidationError
from django.http import HttpResponseRedirect
from .tasks import send_email

UserModel = get_user_model()
class EmailConfirmation:
   
    domain_override=None
    subject_template_name="registration/confirmation_email_subject.txt"
    email_template_name="registration/confirmation_email.html"
    use_https=False
    token_generator=default_token_generator
    from_email=None
    request=None
    html_email_template_name="registration/confirmation_html_email.html"
    extra_email_context=None

    def __init__(self,email,request):
        self.email=email
        self.request=request

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        send_email.delay(
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    )


    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
        )
    def save(self):
        """
        Generate a one-use only link for email confirmation
        """
        if not self.domain_override:
            current_site = get_current_site(self.request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = self.domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(self.email):
            user_email = getattr(user, email_field_name)       
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "username": user.get_username(),
                "token": self.token_generator.make_token(user),
                "protocol": "https" if self.use_https else "http",
                **(self.extra_email_context or {}),
            }
            self.send_mail(
                self.subject_template_name,
                self.email_template_name,
                context,
                self.from_email,
                user_email,
                self.html_email_template_name
            )


INTERNAL_RESET_SESSION_TOKEN = "_confirmation_token"
class EmailConfirmView(TemplateView):
    template_name = "registration/confirmation_done.html"
    reset_url_token = "confirmation-done"
    token_generator = default_token_generator

    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.user.is_active=True
                    self.user.save()

                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "confirmation email unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            UserModel.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": "Password reset unsuccessful",
                    "validlink": False,
                }
            )
        return context