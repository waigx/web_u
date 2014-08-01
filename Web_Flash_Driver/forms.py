from django import forms


class FileForm(forms.Form):
    Password = forms.CharField(widget=forms.PasswordInput, required=False)
    File_File = forms.FileField()


class FileInfoForm(forms.Form):
    file_password = forms.CharField(widget=forms.PasswordInput, required=False)
    file_code = forms.CharField()