from django import template
from website.models import EventMember


register = template.Library()

@register.filter
def get_user_events(user):
    return [i.event for i in EventMember.objects.filter(user=user, event__club__isnull=True)]

@register.filter
def get_user_clubs(user):
    return [i.event for i in EventMember.objects.filter(user=user, event__club__isnull=False)]

@register.filter
def get_role(user):
    ROLES = {
        'student': 'Учащийся',
        'parent': 'Родитель',
        'organizer': 'Организатор'
    }
    return ROLES[user.role]