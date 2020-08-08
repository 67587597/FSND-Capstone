from flask import Flask, request, abort, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import require_auth, AuthError
from models import setup_db, Cases, Donations, Donors, Services
import os
import json
import requests


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)


  @app.route('/main')
  @app.route('/')
  def main():
      return 'test'

  
  @app.route('/cases')
  def get_cases():
    try:
      cases = [case.format() for case in Cases.query.all()]
      print(cases)
      return jsonify({"success": True,
                        "cases": cases
                        }), 200
    except requests.exceptions.HTTPError:
        abort(500)
  
  @app.route('/donations')
  @require_auth('get:donations')
  def get_donations():
    try:
      donations = [donation.format() for donation in Donations.query.all()]
      print(donations)
      return jsonify({"success": True,
                        "donations": donations
                        }), 200
    except requests.exceptions.HTTPError:
        abort(500)


  @app.route('/cases/<case_id>')
  def get_case_detail(case_id):
    try:
      try:
        case = Cases.query.filter_by(id=case_id).one_or_none().format()
        print(case)
      except:
        abort(404)

      return jsonify({"success": True,
                        "cases": case
                        }), 200
    except requests.exceptions.HTTPError:
        abort(500)

  @app.route('/cases', methods=['POST'])
  @require_auth('post:case')
  def add_case():
    try:
      body = request.get_json()
      services =  list(body["services"])
      case = Cases(number=body["number"], issuer=body["issuer"], total_amount=body["total_amount"])
      for service in services:
        case.services.append(Services(description=service["description"], amount=service["amount"], quantity=service["quantity"]))
      case.insert()
      case_id = case.id
      print(case_id)
      # Cases.query.filter_by(number=body["number"]).one_or_none()['id']
      return jsonify({"success": True,
                        "case_id": case_id
                        }), 200
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
        
        return jsonify({"success": True,
                        "donation": donation.id
                        }), 200

      except:
        abort(404)

      
    except requests.exceptions.HTTPError:
        abort(500)
  
  @app.route('/cases/<case_id>', methods=['DELETE'])
  @require_auth('delete:case')
  def delete_case(case_id):
    try:
      
      try:
        case = Cases.query.filter_by(id=case_id).one_or_none()
        print(case + 'to delete')
        case.delete()
        
        return jsonify({"success": True,
                        "case_id": case_id
                        }), 200

      except:
        abort(404)
      
    except requests.exceptions.HTTPError:
        abort(500)
  

  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({"success": False,
                        "message": "resource is not found"
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
    app.run()
