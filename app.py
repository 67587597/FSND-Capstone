from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, abort, jsonify, redirect
from flask_migrate import Migrate
from flask import render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from auth import require_auth, AuthError
from models import setup_db, Cases, Donations, Donors, Services
import os
import json
import requests


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Alow-Hearders",
                             "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, PUT, POST, PATCH, DELETE, OPTIONS")
        return response
        
    # # using the demo intorduced by auth0 here https://auth0.com/docs/quickstart/webapp/python/01-login to implement below auth section
    # oauth = OAuth(app)
    # AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

    # auth0 = oauth.register(
    #     'auth0',
    #     client_id=os.environ['Client_ID'],
    #     client_secret=os.environ['CLIENT_SECERT'],
    #     api_base_url=f'https://{AUTH0_DOMAIN}',
    #     access_token_url=f'https://{AUTH0_DOMAIN}/oauth/token',
    #     authorize_url=f'https://{AUTH0_DOMAIN}/authorize',
    #     client_kwargs={
    #         'scope': 'openid profile email',
    #     },
    # )

    # @app.route('/callback')
    # def callback_handling():
    # # Get response from token endpoint
    #     print('here')
    #     auth0.authorize_access_token()
    #     print(auth0.authorize_access_token())

    #     response = auth0.get('userinfo')
    #     userinfo = response.json()

    #     # Store the user information in flask session.
    #     session['jwt_payload'] = userinfo
    #     session['profile'] = {
    #         'user_id': userinfo['sub'],
    #         'name': userinfo['name']
    #     }
    #     print(session['profile'])
    #     return redirect('/main')

    # @app.route('/login')
    # def login():
    #     return auth0.authorize_redirect(redirect_uri=os.environ['CALLBACK_URL'])
    
    # @app.route('/logout')
    # def logout():
    #     # Clear session stored data
    #     session.clear()
    #     print('logged out successfully')
    #     # Redirect user to logout endpoint
    #     params = {'returnTo': url_for('main', _external=True), 'client_id': os.environ['Client_ID']}
    #     return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/main')
    @app.route('/callback')
    @app.route('/')
    def main():
        # if 'profile' not in session:
        #     print('not in session')
        #     return redirect('/login')
        # return 'Welcome' +  session['profile'].name
        return 'We Donors !'

    @app.route('/cases')
    def get_cases():
        try:
            cases = [case.format() for case in Cases.query.all()]
            # print(cases)
            return jsonify({"success": True, "cases": cases}), 200
        except requests.exceptions.HTTPError:
            abort(500)

    @app.route('/donations')
    @require_auth('get:donations')
    def get_donations():
        try:
            donations = [donation.format() for donation
                         in Donations.query.all()]
            # print(donations)
            return jsonify({"success": True, "donations": donations}), 200
        except requests.exceptions.HTTPError:
            abort(500)

    @app.route('/cases/<case_id>')
    def get_case_detail(case_id):
        try:
            try:
                case = Cases.query.filter_by(id=case_id).one_or_none().format()
                # print(case)
            except:
                abort(404)

            return jsonify({"success": True, "cases": case}), 200
        except requests.exceptions.HTTPError:
            abort(500)

    @app.route('/cases', methods=['POST'])
    @require_auth('post:case')
    def add_case():
        try:
            body = request.get_json()
            services = list(body["services"])
            case = Cases(number=body["number"], issuer=body["issuer"],
                         total_amount=body["total_amount"])
            for serv in services:
                case.services.append(Services(description=serv["description"],
                                     amount=serv["amount"],
                                     quantity=serv["quantity"]))
            case.insert()
            case_id = case.id
            # print(case_id)
            # Cases.query.filter_by(number=body["number"]).one_or_none()['id']
            return jsonify({"success": True, "case_id": case_id}), 200
        except requests.exceptions.HTTPError:
            abort(500)

    @app.route('/cases/<case_id>', methods=['PATCH'])
    @require_auth('patch:case')
    def update_case_paid_amount(case_id):
        try:
            body = request.get_json()
            # case_id = body["case_id"]
            amount = body["amount"]
            try:
                case = Cases.query.filter_by(id=case_id).one_or_none()
                donation = Donations(case_id=case_id, paid_amount=amount)
                donation.insert()
                total_amount = case.total_amount
                if(amount >= total_amount):
                    case.paid = True
                    case.update()
                return jsonify({"success": True, "donation_id": donation.id}), 200

            except:
                abort(404)

        except requests.exceptions.HTTPError:
            abort(500)

    @app.route('/cases/<case_id>', methods=['DELETE'])
    @require_auth('delete:case')
    def delete_case(case_id):
        try:
            case = Cases.query.filter_by(id=case_id).one_or_none()
            # print(case + 'to delete')
            if(case is None):
              abort(404)

            try:
                case.delete()
            except:
                abort(422)
            
            return jsonify({"success": True, "case_id": case_id}), 200
            

        except requests.exceptions.HTTPError:
            abort(500)

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({"success": False, "message": "resource is not found"
                        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                  }), 401

    @app.errorhandler(403)
    def permission_npt_found(error):
        return jsonify({
            "success": False,
            "error": 403,
            "message": "Permission not found"
        }), 401

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False,
                        "error": 400,
                        "message": "Bad request"}), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False,
                        "error": 405,
                        "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"success": False,
                        "error": 500,
                        "message": "Internal server error"}), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({"success": False,
                        "error": error.status_code,
                        "message": error.error}), error.status_code

    return app

APP = create_app()
if __name__ == '__main__':
    # APP.run(host='0.0.0.0', port=8080, debug=True)
    # app.run()
    APP.run()
