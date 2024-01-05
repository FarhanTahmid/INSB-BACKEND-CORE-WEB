from django import forms
import os
from main_website.models import *
from datetime import date

class AchievementForm(forms.ModelForm):
    class Meta:
        model=Achievements
        fields=[
            'award_name','award_winning_year','award_description','award_picture','award_of'
        ]
    
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'award_picture' in self.changed_data:
            previous_instance = Achievements.objects.get(pk=instance.pk)
            previous_picture = previous_instance.award_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.award_picture = instance.award_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance

class NewsForm(forms.ModelForm):
    class Meta:
        model=News
        fields=[
            'news_title', 'news_subtitle', 'news_description','news_picture','news_date'
        ]
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'news_picture' in self.changed_data:
            previous_instance = News.objects.get(pk=instance.pk)
            previous_picture = previous_instance.news_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.news_picture = instance.news_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance
    
class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model=Blog_Category
        fields=[
            'blog_category'
        ]

class BlogsForm(forms.ModelForm):
    class Meta:
        model=Blog
        fields=[
            'title','writer_name','category','date','description','blog_banner_picture',
            'branch_or_society','publish_blog'
        ]
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'blog_banner_picture' in self.changed_data:
            previous_instance = Blog.objects.get(pk=instance.pk)
            previous_picture = previous_instance.blog_banner_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.blog_banner_picture = instance.blog_banner_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance

class ResearchPaperForm(forms.ModelForm):
    class Meta:
        model=Research_Papers
        fields=[
            'title','category','research_banner_picture','author_names','short_description','publication_link','publish_date','publish_research'
        ]
    
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'research_banner_picture' in self.changed_data:
            previous_instance = Research_Papers.objects.get(pk=instance.pk)
            previous_picture = previous_instance.research_banner_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.research_banner_picture = instance.research_banner_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance

class ResearchCategoryForm(forms.ModelForm):
    class Meta:
        model=ResearchCategory
        fields=['category']


class MagazineForm(forms.ModelForm):
    class Meta:
        model=Magazines
        fields=[
            'magazine_title','published_by','publish_date','magazine_short_description','magazine_picture','magazine_file'
        ]
    
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'magazine_picture' in self.changed_data:
            previous_instance = Magazines.objects.get(pk=instance.pk)
            previous_picture = previous_instance.magazine_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)
        if(instance.pk and 'magazine_file' in self.changed_data):
            previous_instance = Magazines.objects.get(pk=instance.pk)
            if(os.path.isfile(previous_instance.magazine_file.path)):
                os.remove(previous_instance.magazine_file.path)

            # Update the instance with the new image
            previous_instance.magazine_picture = instance.magazine_picture
            previous_instance.magazine_file=instance.magazine_file
            previous_instance.save()

        if commit:
            instance.save()
        return instance

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model=GalleryImages
        fields=['image']
        
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)
        
        try:
            new_image=GalleryImages.objects.get(pk=instance.pk)
            pass
        except GalleryImages.DoesNotExist:
            instance.upload_date=date.today()
        
        # Delete the previous image if it exists
        if instance.pk and 'image' in self.changed_data:
            previous_instance = GalleryImages.objects.get(pk=instance.pk)
            previous_picture = previous_instance.image

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)
            # Update the instance with the new image
            previous_instance.image = instance.image
            previous_instance.image=instance.image
            previous_instance.save()

        if commit:
            instance.save()
        return instance

class GalleryVideoForm(forms.ModelForm):
    class Meta:
        model=GalleryVideos
        fields=['video_title','video_link']
    
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)
        
        try:
            new_video=GalleryVideos.objects.get(pk=instance.pk)
            pass
        except GalleryVideos.DoesNotExist:
            instance.upload_date=date.today()
        
        if commit:
            instance.save()
        return instance
    