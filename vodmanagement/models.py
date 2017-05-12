from django.db import models
from django.utils import timezone
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.conf import settings
import humanfriendly
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.urlresolvers import reverse

import os
"""
Copy data in XXX model:
>>> 
from vodmanagement.models import *
objs=Vod.objects.all()
for i in range(0,10):
    newobj=objs[0]
    newobj.pk=None
    newobj.save()    
>>>
This script will copy 10 objs[0] in database
"""
class VodManager(models.Manager):
    def active(self, *args, **kwargs):
        # Post.objects.all() = super(PostManager, self).all()
        return super(VodManager, self)  # .filter(draft=False).filter(publish__lte=timezone.now())


def upload_location(instance, filename):
    # filebase, extension = filename.split(".")
    # return "%s/%s.%s" %(instance.id, instance.id, extension)
    VodModel = instance.__class__
    print('save')
    if VodModel.objects.count() is not 0:
        new_id = VodModel.objects.order_by("id").last().id - 1
    else:
        new_id = 0
    """
    instance.__class__ gets the model Post. We must use this method because the model is defined below.
    Then create a queryset ordered by the "id"s of each object, 
    Then we get the last object in the queryset with `.last()`
    Which will give us the most recently created Model instance
    We add 1 to it, so we get what should be the same id as the the post we are creating.
    """
    print('save image')
    return "%s/%s" % (new_id, filename)

def upload_video_location(instance, filename):
    VodModel = instance.__class__
    if VodModel.objects.count() is not 0:
        new_id = VodModel.objects.order_by("id").last().id +1
    else:
        new_id = 0
    return "%s/videos/%s/%s" %(instance.category.name,new_id,filename)

def upload_image_location(instance, filename):
    VodModel = instance.__class__
    print("path="+instance.category.directory.path)
    if VodModel.objects.count() is not 0:
        new_id = VodModel.objects.order_by("id").last().id +1
    else:
        new_id = 0
    return "%s/images/%s/%s" %(instance.category.name,new_id,filename)


def default_description(instance):
    default = instance.title
    print(default)
    return 'The %s description' % default


# Create your models here.
def default_filedir():
    return settings.MEDIA_ROOT


# ---------------------------------------------------------------------
# if leave path blank,it will save it as the default file dir:settings.MEDIA_ROOT
class FileDirectory(models.Model):
    path = models.CharField(max_length=512,
                            default=default_filedir, blank=True)

    def __str__(self):
        return self.path

    def save(self, *args, **kwargs):
        if self.path is None or self.path == "":
            self.path = default_filedir()
        super(FileDirectory, self).save(*args, **kwargs)


# ---------------------------------------------------------------------
# Two selections only:Common,Special purpose
TYPES = (
    ('common', 'Common'),
    ('special', 'Special purpose'),
)


class VideoCategory(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128,
                            choices=TYPES,
                            default='common'
                            )
    isSecret = models.BooleanField(default=False)
    directory = models.ForeignKey(FileDirectory)  # ,default=FileDirectory.objects.first())

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # print(self.directory)
        #make a folder self.name in the self.directory  
        src = self.directory.path+'/'+self.name
        dst = settings.MEDIA_ROOT+'/'+str(self.name)
        try:
            os.makedirs(src)
        except:
            pass    
        try:
            os.symlink(src,dst)
        except:
            pass
        super(VideoCategory, self).save(*args, **kwargs)

    class Meta:
        # Edit Default Model Name for Human read
        verbose_name_plural = """Video Categorys"""

# ---------------------------------------------------------------------

class Link(models.Model):
    name = models.CharField(max_length=512)
    url = models.TextField(max_length=10240)
    category = models.ForeignKey(VideoCategory, null=True)

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------

class Vod(models.Model):
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to=upload_image_location,
            null=True,
            blank=True)
    video = models.FileField(upload_to=upload_video_location,null=True,blank=False)
    # image = FilerImageField(null=True, blank=True,
    #                         related_name="image_name")
    # video = FilerFileField(null=True, blank=True, related_name="video_name")
    # height_field = models.IntegerField(default=0)
    # width_field = models.IntegerField(default=0)
    category = models.ForeignKey(VideoCategory, null=True)
    # type can be LINK or VOD
    # type = models.CharField(max_length=128,
    #                         choices=(('link','LINK'),('vod','VOD'),),
    #                         default='link')
    status = models.CharField(max_length=128, null=True, blank=True)  # show the data status
    file_size = models.CharField(max_length=128, default='0B', editable=False)
    view_count = models.IntegerField(default=0)
    view_count_temp = 0
    creator = models.ForeignKey(User, null=True, blank=False, editable=False)

    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=250, blank=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)  # The first time added
    custome_time = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True,blank=True)


    objects = VodManager()

    def save(self, *args, **kwargs):
        if self.description is None or self.description == "":
            self.description = default_description(self)
        # if not "http" in self.url:
        #     self.url = "http://" + self.url
        if self.video is not None:
            self.file_size = humanfriendly.format_size(self.video.file.size)
        
        # if self.slug is None or self.slug is "" or not slug_exists(self.slug):
        #     print("save slug")
        #     self.slug = create_slug(self)

        super(Vod, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-timestamp", "-updated"]

    def image_tag(self):
        if self.image is not None and str(self.image) != "":
            print("image:"+str(self.image))
            if os.path.exists(self.image.path):
                 return mark_safe('<img src="%s" width="150" height="200" />' % (self.image.url))
            else:
                return mark_safe('<img src="#" width="150" height="200" />')

    image_tag.short_description = 'Image'

    def get_absolute_url(self):
        return reverse("vod:vod-detail", kwargs={"slug": self.slug})

    def add_view_count(self):
        self.view_count_temp += 1

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Vod.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def slug_exists(slug):
    qs = Vod.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    return exists

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Vod)

"""
from vodmanagement.models import *
objs = Vod.objects.all()
obj = objs.first()

"""