from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_api.models import UserProfile, ResearchReport
from rest_api.es import index_report


# @receiver(post_save, sender=User)
# def default_active_false(sender, instance, created, **kwargs):
#     if created and not instance.is_superuser:
#         instance.is_active = False
#         instance.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(pre_delete, sender=User)
def delete_user_profile(sender, instance, using, **kwargs):
    try:
        UserProfile.objects.get(user=instance).delete()
    except UserProfile.DoesNotExist:
        pass

@receiver(post_save, sender=ResearchReport)
def update_in_elasticsearch(sender, instance, using, **kwargs):
    try:
        index_report(instance)
    except:
        pass