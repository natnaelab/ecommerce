from django.core.cache import cache


def is_user_manager(user):
    if not user.is_authenticated:
        return False

    cache_key = f"user_{user.id}_is_manager"
    is_manager = cache.get(cache_key)
    if is_manager is None:
        is_manager = user.groups.filter(name="Manager").exists()
        cache.set(cache_key, is_manager, timeout=3600)

    return is_manager
