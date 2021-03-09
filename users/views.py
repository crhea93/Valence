from django.shortcuts import render, redirect
from users.forms import CustomUserCreationForm
from block.models import Block
from link.models import Link
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMultiAlternatives
import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import ContactForm, ResearcherSignupForm, ParticipantSignupForm, CustomUserChangeForm
from django.utils import translation
from django.conf import settings as settings_dj
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from io import BytesIO
from tablib import Dataset
import pandas as pd
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from users.models import CAM, Project, CustomUser
from .views_CAM import upload_cam_participant, create_individual_cam, create_individual_cam_randomUser
from users.Plots.DataToPlot import data_to_plot
import datetime
from random_username.generate import generate_username
import re
import base64
User = get_user_model()


@login_required(login_url='loginpage')
def index(request):
    print(datetime.datetime.now())
    if request.method == 'POST':
        print('nope!')
    else:  # request.method = "GET"
        user = request.user
        if user.is_authenticated:
            current_cam = CAM.objects.get(id=user.active_cam_num)
            blocks = current_cam.block_set.all()
            blocks_ = []
            for block in blocks:
                if block.comment is None:
                    block.comment = ''
                blocks_.append(block)
            lines = current_cam.link_set.all()
            lines_ = []
            for line in lines:
                lines_.append(line)
            content = {
            'user':user,
            'existing_blocks':blocks_,
            'existing_lines':lines_
            }
            return render(request, 'base/index.html', content)
        else:
            return redirect('loginpage')


@login_required(login_url='loginpage')
def dashboard(request):
    context = {'projects': Project.objects.all()}
    return render(request, "dashboard.html", context=context)


@login_required(login_url='loginpage')
def tutorials(request):
    context = {}
    return render(request, "tutorials.html", context=context)


@login_required(login_url='loginpage')
def instructions(request):
    context = {}
    return render(request, "instructions.html", context=context)


@login_required(login_url='loginpage')
def contributors(request):
    context = {}
    return render(request, "contributors.html", context=context)


@login_required(login_url='loginpage')
def privacy(request):
    context = {}
    return render(request, "privacy.html", context=context)


@login_required(login_url='loginpage')
def FAQ(request):
    context = {}
    return render(request, "FAQ.html", context=context)

def background(request):
    context = {
        'user': request.user
    }
    if request.user.language_preference == 'de':
        return render(request, "Background-Nav/Background_German.html", context=context)
    else:
        return render(request, "Background-Nav/Background.html", context=context)


def background_german(request):
    context = {
        'user': request.user
    }
    return render(request, "Background-Nav/Background_German.html", context=context)


def loginpage(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        print(form)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print(user.is_researcher)
                if user.is_researcher:
                    return redirect('dashboard')
                else:
                    return redirect('dashboard')
            else:
                pass
        else:
            message = ''
            username = form.data.get('username')
            password = form.data.get('password')
            if username not in User.objects.values_list('username', flat=True):
                message = _('Username does not exist')
            elif authenticate(username=username, password=password):
                message = _('Username or Password is incorrect')
            else:
                message = _('User is not authenticated. Check your emails to validate your account.')
            return render(request=request,
                          template_name="registration/login.html",
                          context={"form": form, 'message': message})
    form = AuthenticationForm()
    return render(request=request,
                  template_name="registration/login.html",
                  context={"form": form})


def signup(request):
    """This view accept deals with the account creation form.
    In POST mode, it accepts the account creation form, validates it,
    create the user in the DB if the form is valid and sends an email with
    the token to activate the account.
    In GET mode, it renders the form template for the account registration:
    'registration/register.html'.
    """
    formParticipant = ParticipantSignupForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            # Save user
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            login(request, user)
            return render(request, "index.html")
        else:
            context = {
                'message': form.errors,
                "form": form,
                'formParticipant': formParticipant,
                'projects': Project.objects.all()
            }
            return render(request, 'registration/register.html', context=context)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', context={'form': form, 'projects': Project.objects.all()})

def create_participant(request):
    if request.method == 'POST':
        form = ParticipantSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            # Set project
            project_name = request.POST.get('project_name')
            project_password = request.POST.get('project_password')
            project = Project.objects.get(name=project_name)
            print(project_password, project.password)
            if project_password == project.password or project.password == 'None' or project.password is None or project.password == project_name:
                user.project = project_name
                user.save()
                print('uploading CAM')
                upload_cam_participant(user, project)
                return redirect('index')
            else:
                print('NO!')
                return redirect('dashboard')
            # Create CAM

        else:
            context = {
                'message': form.errors,
                "form": form,
                'projects': Project.objects.all()
            }
            return render(request, 'registration/register.html', context=context)
    '''
    if request.method == 'POST':
        form = ParticipantSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            # Set project

            if request.POST.get('project_password') != 'None':
                project_name = request.POST.get('project_name')
                project_password = request.POST.get('project_password')
                project = Project.objects.get(name=project_name)
                if project_password == project.password or project.password == 'None' or project.password is None:
                    user.project = project_name
                    user.save()
                    print('uploading CAM')
                    upload_cam_participant(user, project)
                    return redirect('index')
                else:
                    return redirect('dashboard')
            # Create CAM
            else:
                create_individual_cam(request)
                return redirect('index')


        else:
            context = {
                'message': form.errors,
                "form": form,
                'projects': Project.objects.all()
            }
            return render(request, 'registration/register.html', context=context)
    '''
def join_project(request):
    project_name = request.POST.get('project_name')
    project = Project.objects.get(name=project_name)
    print('Project checked: '+request.POST.get('project_checked'))
    if request.POST.get('project_checked') == 'true':
        if request.POST.get('project_password') == project.password:
            upload_cam_participant(request.user, project)
            return JsonResponse({"message": "Success"})
        else:
            return  JsonResponse({"message": "Failure"})
    else:
        create_individual_cam(request)
        return redirect('index')


def create_researcher(request):
    if request.method == 'POST':
        form = ResearcherSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            create_individual_cam(request)
            return redirect('index')
        else:
            context = {
                'message': form.errors,
                "form": form
            }
            return render(request, 'registration/register.html', context=context)


def clear_CAM(request):
    clear_cam_valid = request.POST.get('clear_cam_valid')  # clear cam
    if clear_cam_valid:
        # clear blocks associated with user
        current_cam = CAM.objects.get(id=request.user.active_cam_num)
        blocks = current_cam.block_set.all()
        for block in blocks:
            block.delete()
        # clear links associated with user
        links = current_cam.link_set.all()
        for link in links:
            link.delete()
        return HttpResponse()


"""def Image_CAM(request):
    '''
    For more pdf options look at wkhtmltopdf documentation
    :param request:
    :return:
    '''
    user = User.objects.get(name=request.user.username)
    file_name = 'media/CAMS/'+user.username+'_'+str(user.active_cam_num)+'.png'
    data_to_plot(user.username,file_name)
    user = CustomUser.objects.get(id=user.id)
    current_cam = CAM.objects.get(id=user.active_cam_num)
    current_cam.cam_image = file_name
    current_cam.save()
    return JsonResponse({'file_name': '../../'+file_name})"""

def Image_CAM(request):
    '''
    For more pdf options look at wkhtmltopdf documentation
    :param request:
    :return:
    '''
    #config = pdfkit.configuration(wkhtmltopdf='./bin/wkhtmltopdf')
    image_data = request.POST.get('html_to_convert')
    print(request.user)
    print(request.user.active_cam_num)
    file_name = 'media/CAMS/'+request.user.username+'_'+str(request.user.active_cam_num)+'.png'
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    image_data = dataUrlPattern.match(image_data).group(2)
    image_data = image_data.encode()
    image_data = base64.b64decode(image_data)
    with open(file_name, 'wb') as f:
        f.write(image_data)
    current_cam = CAM.objects.get(id=request.user.active_cam_num)
    current_cam.cam_image = file_name
    current_cam.save()
    print('Saved')
    return JsonResponse({'file_name': '../../'+file_name})

    #return JsonResponse({'file_name': file_name})


def view_pdf(request):
    print('meow meow')
    User = get_user_model()
    user = User.objects.get(username=request.user.username)
    content = {
        'user': user,
    }
    return render(request, 'Background-Nav/PDF_view.html', content)


def export_CAM(request):
    current_cam = CAM.objects.get(id=request.user.active_cam_num)
    block_resource = BlockResource().export(current_cam.block_set.all()).csv
    link_resource = LinkResource().export(current_cam.link_set.all()).csv
    outfile = BytesIO()  # io.BytesIO() for python 3
    names = ['blocks', 'links']
    ct = 0
    with ZipFile(outfile, 'w') as zf:
        for resource in [block_resource,link_resource]:
            zf.writestr("{}.csv".format(names[ct]), resource)
            ct += 1
    response = HttpResponse(outfile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="'+request.user.username+'_CAM.zip"'
    return response


def import_CAM(request):
    if request.method == 'POST':
        block_resource = BlockResource()
        link_resource = LinkResource()
        dataset = Dataset()
        uploaded_CAM = request.FILES['myfile']
        deletable = request.POST.get('Deletable')
        # Clear all current blocks and links
        current_cam = CAM.objects.get(id=request.user.active_cam_num)
        user = request.user
        blocks = current_cam.block_set.all()
        for block in blocks:
            block.delete()
        links = current_cam.link_set.all()
        for link in links:
            link.delete()
        ct = 0
        print(current_cam)
        try:
            with ZipFile(uploaded_CAM) as z:
                for filename in z.namelist():
                    if filename.endswith('.csv'):
                        data = z.extract(filename)
                        test = pd.read_csv(data)
                        print(test)
                        #test['id'] = test['id'].apply(lambda x: ' ')  # Must be empty to auto id
                        test['creator'] = test['creator'].apply(lambda x: request.user.id)
                        test['CAM'] = test['CAM'].apply(lambda x: current_cam.id)
                        test.to_csv(data)
                        imported_data = dataset.load(open(data).read())
                        if ct == 0:
                            result = block_resource.import_data(imported_data, dry_run=True)  # Test the data import
                            if not result.has_errors():
                                block_resource.import_data(imported_data, dry_run=False)  # Actually import now
                            else:
                                print('sad')
                        else:
                            result = link_resource.import_data(imported_data, dry_run=True)  # Test the data import
                            if not result.has_errors():
                                link_resource.import_data(imported_data, dry_run=False)  # Actually import now
                        ct += 1
                    else:
                        pass
        except:
            print('didnt work')
        # We now have to clean up the blocks' links...
        blocks_imported = current_cam.block_set.all()
        print(blocks_imported)
        for block in blocks_imported:
            # Clean up Comments ('none' -> '')
            if block.comment == 'None' or block.comment == 'none':
                block.comment = ''
            if deletable is not None:
                block.modifiable = False
            # Change block creator to current user
            block.creator = request.user
            block.save()
        links_imported = current_cam.link_set.all()

        for link in links_imported:
            link.creator = request.user
            link.save()
        return redirect('/')


def contact_form(request):
    contact_form = None
    if request.method == 'GET':
        contact_form = ContactForm()
        return render(request, 'Admin/Contact_Form_2.html')
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            # Send email
            html_content = render_to_string(
                'Admin/email_contact_us.html',
                {'contacter': contact_form.cleaned_data['contacter'],
                 'email': contact_form.cleaned_data['email'],
                 'message': contact_form.cleaned_data['message']})
            text_content = strip_tags(html_content)
            email_subject = 'CAM'
            email_from = contact_form.cleaned_data['email']
            message = EmailMultiAlternatives(
                email_subject, text_content, email_from, ['thibeaultrheaprogramming@gmail.com']
            )
            message.attach_alternative(html_content, 'text/html')
            message.send()
            return HttpResponse('done')


def send_cam(request):
    user_id = request.user.id
    username = request.user.username
    html_content = render_to_string(
        'Admin/send_CAM.html',
        {'contacter': username})
    text_content = strip_tags(html_content)
    email_subject = request.user.username+"'s CAM"
    email_from = 'thibeaultrheaprogramming@gmail.com'
    message = EmailMultiAlternatives(
        email_subject, text_content, email_from, ['thibeaultrheaprogramming@gmail.com']
    )
    message.attach_alternative(html_content, 'text/html')
    block_resource = BlockResource().export(Block.objects.filter(creator=user_id)).csv
    link_resource = LinkResource().export(Link.objects.filter(creator=user_id)).csv
    message.attach(username+'_blocks.csv', block_resource, 'text/csv')
    message.attach(username+'_links.csv', link_resource, 'text/csv')
    message.attach(username+'_CAM.pdf', open('media/'+username+'.pdf', 'rb').read())
    message.send()
    return redirect('/')


def language_change(request):
    if request.method == 'POST':
        # Change current language
        user_language = request.POST.get('language')
        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        # Update users language preference
        print(user_language)
        if str(request.user) != 'AnonymousUser':
            user_ = request.user
            user_.language_preference = user_language
            user_.save()
        response = HttpResponse(...)
        response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user_language)
        print('Successful')
        return HttpResponse('Language successfully changed')
    else:
        return HttpResponse('Language successfully changed')


def language_change_anonymous(request):
    # Change current language
    user_language = request.LANGUAGE_CODE
    if user_language == 'en':
        user_language = 'de'
    elif user_language == 'de':
        user_language = 'en'
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    # Update users language preference
    response = HttpResponse(...)
    response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user_language)
    return redirect(request.META['HTTP_REFERER'])


#@login_required(login_url='login')
def settings(request):
    """This view is the user settings view.
    Depending of the request, we want to either show the user's settings
    or change them. In either case, we re-render the same page with
    the final settings.
    """
    user = request.user
    if request.method == 'POST':
        avatar_ = request.FILES.get('id_image')
        print(avatar_)
        if avatar_:
            user.avatar = avatar_
        form = CustomUserChangeForm(request.POST, instance=user)
        # need to validate form before accessing cleaned data
        if form.is_valid():
            form.save()
        else:
            pass
    else:  # request.method == "GET"
        form = CustomUserChangeForm(instance=user)
    content = {
        'user': user,
        'form': form
    }
    return render(request, 'settings_account.html', content)


def delete_user(request):
    """
    Simple view to delete user
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
    else:
        user_id = request.GET.get('user_id')
    user = User.objects.get(id=user_id)
    user.delete()
    return HttpResponse('User Deleted')


def create_random(request):
    """
    Create user with randomized username and password
    """
    if request.method == 'POST':
        username_ = generate_username(1)[0]
        print(username_)
        user = User.objects.create(username=username_, password=username_[::-1], random_user=True)
        login(request, user)
        create_individual_cam_randomUser(request, user)
        return redirect('index')


