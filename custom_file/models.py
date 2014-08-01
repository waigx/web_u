from django.db import models

# Create your models here.


class File(models.Model):
    File_Name = models.CharField(max_length=255)
    File_Code = models.CharField(max_length=255)
    Is_Protected = models.BooleanField()
    Hashed_Password = models.CharField(max_length=255)
    Uploaded_Time = models.DateField()
    File_File = models.FileField(upload_to='files_storage/')