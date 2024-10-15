from flask import redirect, url_for, session, request, flash
from google_auth_oauthlib.flow import Flow

class GoogleDrivePage:
    route = '/gdrive'
    methods = ['GET']
    endpoint_name = 'google_drive'

    @staticmethod
    def view_func():
        flow = Flow.from_client_secrets_file('client_secret.json', scopes=['https://www.googleapis.com/auth/drive'])
        flow.redirect_uri = url_for('oauth2callback', _external=True)

        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        session['state'] = state
        return redirect(authorization_url)


class GoogleDriveCallbackPage:
    route = '/oauth2callback'
    methods = ['GET']
    endpoint_name = 'oauth2callback'

    @staticmethod
    def view_func():
        """Handle the OAuth2 callback after user authenticates with Google"""
        # OAuth callback logic here
        state = session.get('state')
        flow = Flow.from_client_secrets_file('client_secret.json', scopes=['https://www.googleapis.com/auth/drive'], state=state)
        flow.redirect_uri = url_for('oauth2callback', _external=True)

        # Exchange authorization code for tokens
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in session
        credentials = flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        flash('Successfully authenticated with Google Drive!', 'success')
        next_action = session.get('action','upload')
        return redirect(url_for(next_action))  # Redirect to the next step
