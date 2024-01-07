from django.db import models
from django.core.files.storage import FileSystemStorage
from port.models import Chapters_Society_and_Affinity_Groups
from django_resized import ResizedImageField
from PIL import Image
from ckeditor.fields import RichTextField
from users.models import Members
# Create your models here.
    
# Tables for Homepage
class HomePageTopBanner(models.Model):
    banner_picture=ResizedImageField(null=False,blank=False,upload_to='main_website_files/homepage/banner_pictures')
    first_layer_text=models.CharField(null=False,blank=False,default="FOCUSING LIMELIGHT ON",max_length=50)
    first_layer_text_colored=models.CharField(null=False,blank=False,default="MASTERMINDS",max_length=20)
    third_layer_text=models.TextField(null=False,blank=False,max_length=200)
    button_text=models.CharField(null=False,blank=False,max_length=50,default="About INSB")
    button_url=models.CharField(null=False,blank=False,default="#",max_length=200)
    class Meta:
        verbose_name='Homepage Banner Picture With Texts'
    def __str__(self) -> str:
        return str(self.pk)

#Table for Ribbon Picture
class BannerPictureWithStat(models.Model):

    image = ResizedImageField(upload_to='main_website_files/homepage/ribbon_picture')
    
    class Meta:
        verbose_name="Banner Picture with Statistics in Homepage"
    
    def __str__(self) -> str:
        return str(self.pk)

class ResearchCategory(models.Model):
    category=models.CharField(null=False,blank=False,max_length=100)

    class Meta:
        verbose_name='Research Category'
    def __str__(self) -> str:
        return str(self.category)

#Table for Research Papers
class Research_Papers(models.Model):
    title = models.CharField(null=False,blank=False,max_length=200)
    category=models.ForeignKey(ResearchCategory,null=True,blank=True,on_delete=models.CASCADE)
    research_banner_picture = models.ImageField(null=False,blank=False,default='main_website_files/Research_pictures/default_research_banner_picture.png',upload_to='main_website_files/Research_pictures/')
    author_names = RichTextField(null=False,blank=False,max_length=300)
    short_description=RichTextField(null=False,blank=False,max_length=500)
    publish_date=models.DateField(null=False,blank=False,help_text = "<br>Please use the following format: <em>YYYY-MM-DD</em>.")
    publication_link = models.URLField(null=False)
    publish_research=models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name = "Research Paper"
    def __str__(self):
        return f"{self.title} {self.author_names}"


    
#Table fot blog category
class Blog_Category(models.Model):
    blog_category = models.CharField(max_length=40,null=False,blank=False)

    def __str__(self):
        return self.blog_category
    
#Table for Blogs
class Blog(models.Model):
    ieee_id=models.IntegerField(null=True,blank=True)
    writer_name=models.CharField(null=False,blank=False,max_length=50)
    title = models.CharField(null=False,blank=False,max_length=150)
    category = models.ForeignKey(Blog_Category,null=True,blank=True,on_delete=models.CASCADE)
    date = models.DateField(null=False,blank=False,help_text = "<br>Please use the following format: <em>YYYY-MM-DD</em>.")
    short_description=RichTextField(null=False,blank=False,max_length=200,help_text="Write within 50 words!")
    blog_banner_picture = ResizedImageField(null=False,blank=False,default='main_website_files/Blog_banner_pictures/default_blog_banner_picture.png',upload_to='main_website_files/Blog_pictures/')
    description = RichTextField(null=False,blank=False,max_length=5000,help_text="Write within 500 words!")
    branch_or_society = models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    publish_blog=models.BooleanField(null=False,blank=False,default=False)
    is_requested=models.BooleanField(null=True,blank=True)
    class Meta:
        verbose_name = "Blog"
    def __str__(self):
        return self.title

#Table for Achievements
class Achievements(models.Model):
    award_name=models.CharField(null=False,blank=False,max_length=100)
    award_description=RichTextField(null=True,blank=True,max_length=1000)
    award_winning_year=models.IntegerField(null=False,blank=False)
    award_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,on_delete=models.CASCADE)
    award_picture=models.ImageField(null=False,blank=False,upload_to='main_website_files/achievements/')
    
    class Meta:
        verbose_name="Achievements"
    
    def __str__(self) -> str:
        return str(self.pk)

# Table for news
class News(models.Model):
    news_title=models.CharField(null=False,blank=False,max_length=150)
    news_subtitle=models.CharField(null=True,blank=True,max_length=100)
    news_description=RichTextField(null=False,blank=False,max_length=500)
    news_picture=models.ImageField(null=False,blank=False,upload_to='main_website_files/news/')
    news_date=models.DateField(null=True,blank=True,help_text = "Please use the following format: <em>YYYY-MM-DD</em>.")
    
    class Meta:
        verbose_name="News"
    def __str__(self) -> str:
        return str(self.pk)

# Table for Magazine
class Magazines(models.Model):
    magazine_title=models.CharField(null=False,blank=False,max_length=100)
    published_by=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE)
    publish_date=models.DateField(null=False,blank=False,help_text = "<br>Please use the following format: <em>YYYY-MM-DD</em>.")
    magazine_short_description=RichTextField(null=False,blank=False,max_length=400)
    magazine_picture=ResizedImageField(null=False,blank=False,upload_to="main_website_files/magazine_pictures/")
    magazine_file=models.FileField(null=False,blank=False,upload_to="main_website_files/Magazine/")
    
    class Meta:
        verbose_name="Magazine"
    def __str__(self) -> str:
        return self.magazine_title
    
class IEEE_Bangladesh_Section(models.Model):
    about_ieee_bangladesh = models.TextField(null=True,blank=True)
    ieee_bangladesh_logo = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE Bangladesh Section/logo/")
    member_and_volunteer_description = models.TextField(null=True,blank=True)
    member_and_volunteer_picture = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE Bangladesh Section/member_volunteer_picture/")
    benefits_description = models.TextField(null=True,blank=True)
    student_branches_description = models.TextField(null=True,blank=True)
    affinity_groups_description = models.TextField(null=True,blank=True)
    community_and_society_description = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name="IEEE Bangladesh Section"
    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists
        self.id = 1  # Set the primary key to 1 to always update the same row
        super(IEEE_Bangladesh_Section, self).save(*args, **kwargs)
    def __str__(self) -> str:
        return str(self.pk)
    
class About_IEEE(models.Model):
    about_ieee = models.TextField(null=True,blank=True)
    about_image = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE/About Image/")
    community_description = models.TextField(null=True,blank=True)
    community_image = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE/Community Image/")
    start_with_ieee_description = models.TextField(null=True,blank=True)
    collaboration_description = models.TextField(null=True,blank=True)
    publications_description = models.TextField(null=True,blank=True)
    events_and_conferences_description = models.TextField(null=True,blank=True)
    achievements_description = models.TextField(null=True,blank=True)
    innovations_and_developments_description = models.TextField(null=True,blank=True)
    innovations_and_developments_image = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE/Innovation Development Image/")
    students_and_member_activities_description = models.TextField(null=True,blank=True)
    students_and_member_activities_image = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE/Student Member Activity Image/")
    quality_description = models.TextField(null=True,blank=True)
    quality_image = ResizedImageField(null=True,blank=True,upload_to="main_website_files/About/IEEE/Quality Image/")

    class Meta:
        verbose_name="About IEEE"
    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists
        self.id = 1  # Set the primary key to 1 to always update the same row
        super(About_IEEE, self).save(*args, **kwargs)
    def __str__(self) -> str:
        return str(self.pk)

# class IEEE_Bangladesh_Section_Links(models.Model):

#     links = models.URLField(null=True,blank=True,default="www.nolinkgiven.com")

#     class Meta:
#         verbose_name="IEEE BD Section Link"
#     def __str__(self) -> str:
#         return self.pk
    
class IEEE_Bangladesh_Section_Gallery(models.Model):

    picture = ResizedImageField(null=False,blank=False,upload_to="main_website_files/About/IEEE Bangladesh Section/Gallery/")

    class Meta:
        verbose_name="IEEE Bangladesh Section Gallery"
    def __str__(self) -> str:
        return self.pk

class HomePage_Thoughts(models.Model):

    quote = models.TextField(null=False,blank=False)
    author = models.CharField(null=False,blank=False,max_length=500)#can be a foreign key to a faculty
    
    class Meta:
        verbose_name="HomePage Thoughts"
    def __str__(self) -> str:
        return self.author
    
class GalleryImages(models.Model):
    image=ResizedImageField(null=False,blank=False,upload_to='main_website_files/gallery_pictures/')
    upload_date=models.DateField(null=False,blank=False)
    
    class Meta:
        verbose_name = "Gallery Image"
    def __str__(self) -> str:
        return str(self.pk)

class GalleryVideos(models.Model):
    video_title=models.CharField(null=False,blank=False,max_length=100)
    video_link=models.URLField(null=False,blank=False,help_text="Please use embed link if you are pasting a link of Youtube video!")
    upload_date=models.DateField(null=False,blank=False)

    class Meta:
        verbose_name="Gallery Video"
    def __str__(self) -> str:
        return str(self.pk)

class ExemplaryMembers(models.Model):
    member_name=models.CharField(null=False,blank=False,max_length=100)
    member_picture=models.ImageField(null=True,blank=True,upload_to='main_website_files/exemplary_members_picture/')
    former_position=models.CharField(null=True,blank=True,max_length=100)
    activity_year=models.CharField(null=True,blank=True,max_length=50)
    current_activity=models.CharField(null=True,blank=True, max_length=200)
    facebook_account_link=models.URLField(null=True,blank=True,max_length=200)
    email=models.EmailField(null=True,blank=True)
    achievements=RichTextField(null=True,blank=True,max_length=1000)
    rank=models.IntegerField(null=True,blank=True,help_text="This is used to sort exemplary members in the main website")
    class Meta:
        verbose_name="Exemplary Members"

    def __str__(self) -> str:
        return self.member_name

