from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponse
from django.views import View
from django.shortcuts import redirect
from SpotifyController.services.spotify_auth import AuthService
from User.services import UserService

from SpotifyController.services.aggregator.aggregator_base import BaseUserAggregator
from SpotifyController.services.aggregator.create_user_recommendation_playlist import CreateUserRecommendationPlaylist
from SpotifyController.services.aggregator.create_top_tracks_playlist import CreateTopTracksPlaylist

import logging

logger = logging.getLogger(__name__)

class SpotifyLoginView(View):
    @staticmethod
    def get(request):
        """
        Handles the OAuth authorization process by generating an authorization URL
        and redirecting the user to it.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object received from the client.

        Returns
        -------
        HttpResponseRedirect
            A redirection to the constructed authorization URL.

        """

        sp_oauth = AuthService.oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

class SpotifyCallbackView(View):
    @staticmethod
    def get(request):
        """
        Handles Spotify user authentication and updates the user information in the database,
        including token retrieval and user session management. Redirects the user
        to appropriate views based on the authentication and user status.

        Parameters:
            request: HttpRequest
                The HTTP request object containing user, session, and GET data.

        Raises:
            None

        Returns:
            HttpResponseRedirect
                A redirect response to the appropriate URL, such as 'login',
                'confirm_register' or 'profile'.
        """ 

        code = request.GET.get('code')

        sp_oauth = AuthService.oauth()
        token_info = sp_oauth.get_access_token(code)
        access_token, refresh_token, expires_at = AuthService.get_tokens(token_info)

        user = request.user
        user_logged_in = user if user.is_authenticated else None

        result = UserService.spotify_update_user(
            access_token,
            refresh_token,
            expires_at,
            user_logged_in
        )

        if result.error:
            messages.error(request, result.error)
            return redirect("login")

        if not result.is_existing and result.data:
            request.session['spotify_user_info'] = result.data
            return redirect("confirm_register")

        if not user_logged_in:
            login(request, result.user)
            logger.info("User logged in: login=%s user_id=%s", result.user.user_login, result.user.id)

        logger.debug("Redirecting to profile: user_id=%s", result.user.id)
        return redirect('profile', user_id = result.user.id)

class CreateSpotifyPlaylistView(View):
    @staticmethod
    def post(request):
        """
        Handles a POST request to create a user recommendation playlist for the authenticated user.

        This static method processes a request to create a recommendation playlist for the authenticated user. If the user is authenticated, it initializes a `BaseUserAggregator` with the user, executes the `CreateUserRecommendationPlaylist` service for the user, and returns an HTTP status 200 response. If the user is not authenticated, it returns an HTTP status 401 response.

        Arguments:
            request: The HTTP request object containing user information.

        Returns:
            HttpResponse: A response with status 200 if the user is authenticated,
            otherwise a response with status 401.
        """

        user = request.user

        if user:
            base_user_aggregator = BaseUserAggregator(users=[user])
            base_user_aggregator.run_services_for_each_user(CreateUserRecommendationPlaylist)
            return HttpResponse(status=200)

        return HttpResponse(status=401)

class CreateSpotifyPlaylistTopTracksView(View):
    @staticmethod
    def post(request):
        """
        Executes the logic to create top tracks playlists for the authenticated
        user if available. Returns appropriate HTTP response based on the user's
        authentication status.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: An HTTP response with the status code 200 if a user is
            authenticated and the operation is successful, or 401 if the user is
            not authenticated.
        """

        user = request.user

        if user:
            base_user_aggregator = BaseUserAggregator(users=[user])
            base_user_aggregator.run_services_for_each_user(CreateTopTracksPlaylist)
            return HttpResponse(status=200)

        return HttpResponse(status=401)