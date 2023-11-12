from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
	parent=models.ForeignKey('self',default=None,null=True,blank=True,on_delete=models.SET_NULL,related_name='children')
	title=models.CharField(max_length=200)
	slug=models.SlugField(max_length=200,unique=True)
	status=models.BooleanField(default=True)

	class Meta:
		verbose_name_plural='Categories'
		ordering=['parent__id']
	def __str__(self):
		return self.title

class Post(models.Model):
	STATUS_CHOICE=[
		('d','draft'),
		('p','publish'),
		('r','reject'),
		('i','investigate')

	]

	title=models.CharField(max_length=200)
	slug=models.SlugField(max_length=200,unique=True)
	author=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL,related_name='articles')
	category=models.ManyToManyField(Category,related_name='articles')
	description=models.TextField()
	thumbnail=models .ImageField(upload_to='article-image')
	published=models.DateTimeField(default=timezone.now)
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	status=models.CharField(max_length=1,choices=STATUS_CHOICE)

	def __str__(self):
		return self.title

	class Meta:
		ordering=['published']