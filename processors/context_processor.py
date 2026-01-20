def user_header_data(request):
    user = request.user

    if user.is_authenticated:
        return {
            "header_user": {
                "name": user.username,
                "image": getattr(user, "image", None),
                "id": user.id,
            }
        }

    return {
        "header_user": None
    }