from django.http import StreamingHttpResponse, HttpResponse

from django.shortcuts import render_to_response
from django.core.servers.basehttp import FileWrapper
from random import randint
from datetime import datetime
from django.utils.encoding import smart_str
from hashlib import md5
import os
import json
import mimetypes

from custom_file.models import File
from .forms import FileForm, FileInfoForm


# Create your views here.


def get_random_file_code():
    min_length = 1
    already_exists = True
    repeat_times = 0
    random_code = ''
    while already_exists:
        random_code = ''
        for i in range(min_length):
            seed = randint(55, 90)
            if seed < 65:
                random_code += str(seed - 55)
            else:
                random_code += chr(seed)
        try:
            File.objects.get(File_Code=random_code)
        except File.DoesNotExist:
            already_exists = False
        else:
            repeat_times += 1

        if repeat_times >= 3:
            min_length += 1
            repeat_times = 0

    return random_code


def hash_password(file_name, password, file_code):
    return str(md5(str(md5((file_name + password + file_code).encode('utf-8')).hexdigest())).hexdigest())


def main(request):
    new_user = True
    new_file_code = request.POST.get('file_code', None)
    new_file_password = request.POST.get('file_password', '')
    new_file_file = request.FILES.get('uploaded_file', None)

    if request.method == 'POST':
        if new_file_file is None and new_file_code is None:
            old_file_code = request.POST.get('old_file_code', None)

            if old_file_code is None:
                fail_reason = 'File code could not be empty'
                result = ({"is_success": False,
                           "fail_reason": fail_reason, })
                return HttpResponse(json.dumps(result), content_type='application/json')
            else:
                old_file_code = old_file_code.upper()

            try:
                queried_file = File.objects.get(File_Code=old_file_code)
            except File.DoesNotExist:
                fail_reason = 'File code does not exists.'
                result = ({"is_success": False,
                           "fail_reason": fail_reason, })
                return HttpResponse(json.dumps(result), content_type='application/json')
            else:
                result = ({"is_success": True, })
                return HttpResponse(json.dumps(result), content_type='application/json')

        if new_file_code is not None:
            new_file_code = new_file_code.upper()
            for i in new_file_code:
                if (ord(i) > 90) or (ord(i) < 48) or (57 < ord(i) < 65):
                    fail_reason = 'The letter must between A~Z or 1~9.'
                    result = ({"is_success": False,
                               "fail_reason": fail_reason, })
                    return HttpResponse(json.dumps(result), content_type='application/json')

            new_file_info = FileInfoForm(request.POST)
            already_exists = True
            if new_file_code != request.session['code']:
                try:
                    File.objects.get(File_Code=new_file_code)
                except File.DoesNotExist:
                    already_exists = False
            else:
                already_exists = False

            if already_exists:
                fail_reason = 'The code is already existed.'
                result = ({"is_success": False,
                           "fail_reason": fail_reason, })
                return HttpResponse(json.dumps(result), content_type='application/json')

            queried_file = File.objects.get(File_Code=request.session['code'])
            queried_file.File_Code = new_file_code

            if new_file_password == '':
                queried_file.Is_Protected = False
            else:
                queried_file.Is_Protected = True
                queried_file.Hashed_Password = hash_password(queried_file.File_Name, new_file_password, new_file_code)

            request.session['password'] = new_file_password
            request.session['code'] = new_file_code

            queried_file.save()
            result = ({"is_success": True,
                       "code": new_file_code, })
            return HttpResponse(json.dumps(result), content_type='application/json')

        else:
            new_file_code = get_random_file_code()
            new_file_name = new_file_file.name
            new_file_password = ''
            new_file_protected = False

            request.session['name'] = new_file_name
            request.session['code'] = new_file_code
            request.session['password'] = ''

            new_file = File(
                File_Name=new_file_name,
                File_Code=new_file_code,
                Is_Protected=new_file_protected,
                Hashed_Password=hash_password(new_file_name, new_file_password, new_file_code),
                Uploaded_Time=datetime.now(),
                File_File=new_file_file, )

            new_file.save()

            result = ({"name": new_file_name,
                       "size": new_file_file.size,
                       "code": new_file_code, })

            response_data = json.dumps(result)
            return HttpResponse(response_data, content_type='application/json')

    return render_to_response('main.html', locals())


def main_old(request):
    if request.method == "POST":
        new_file_upload = FileForm(request.POST, request.FILES)
        if new_file_upload.is_valid():
            new_file_basic_info = new_file_upload.cleaned_data
            new_file_code = get_random_file_code()
            new_file_name = request.FILES['File_File'].name
            new_file_password = new_file_basic_info['Password']
            new_file_protected = True

            request.session['password'] = new_file_password
            request.session['name'] = new_file_name
            request.session['code'] = new_file_code

            if new_file_password == '':
                new_file_protected = False

            new_file = File(
                File_Name=new_file_name,
                File_Code=new_file_code,
                Is_Protected=new_file_protected,
                Hashed_Password=hash_password(new_file_name, new_file_password, new_file_code),
                Uploaded_Time=datetime.now(),
                File_File=request.FILES['File_File'], )

            new_file.save()
            success_upload_code = new_file_code
            success_upload_flag = True
        else:
            success_upload_flag = False
    else:
        new_user = True
        new_file_upload = FileForm()

    return render_to_response('main_old.html', locals())


def download(request, file_id):
    file_id = file_id.upper()

    has_permission = False

    try:
        queried_file = File.objects.get(File_Code=file_id)
    except File.DoesNotExist:
        is_file_exists = False
        return render_to_response('file_not_exists.html', locals())

    else:
        is_file_exists = True
        title = "Download " + queried_file.File_Name

        if request.method == "POST":
            session_password = request.POST['Password']
            panel_style = "panel-danger"
            hint = "Password error, please enter the correct password."
        else:
            session_password = request.session.get('password', '')
            panel_style = "panel-warning"
            hint = "You don't have the permission, enter password to continue."

        if queried_file.Is_Protected:
            if (request.method == "POST" or request.session.get('code', '') == queried_file.File_Code)\
                    and queried_file.Hashed_Password == hash_password(queried_file.File_Name,
                                                                      session_password,
                                                                      queried_file.File_Code):
                has_permission = True
        else:
            has_permission = True

    if has_permission:
        request.session['password'] = session_password
        file_path = queried_file.File_File.path
        wrapper = FileWrapper(open(file_path, "r"))
        content_type = mimetypes.guess_type(file_path)[0]
        if content_type is None:
            content_type = 'application/force-download'

        queried_file_name = queried_file.File_Name
        if request.META.get('HTTP_USER_AGENT', None).find('MSIE') < 0:
            queried_file_name = queried_file_name.encode('gb2312')

        response = StreamingHttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(queried_file_name)
        return response
    else:
        return render_to_response('permission_denied.html', locals())