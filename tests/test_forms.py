# USAGE
# pytest -v --no-header tests/test_forms.py | tee results.txt

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
def extract_csrf_token(content):
    match = re.search(
        r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', 
        content)
    if match:
        return match.group(1)
    return None

# ---

from app import app
from forms import (
    GetScoreData,
    GetNewScore,
)

from datetime import date

def test_GetScoreData_empty():
    with app.test_request_context('/'):
        form = GetScoreData()
        assert not form.validate()
        assert form.errors
        
def test_GetScoreData_valid():
    with app.test_request_context('/'):
        with app.test_client() as client:
            response = client.get('/')
            csrf_token = extract_csrf_token(response.data.decode("utf-8"))

            form = GetScoreData(
                season = "outdoors",
                distance = 50,
                units = "1",
                days_till = date.today(),
                is_comp = True,
                csrf_token = csrf_token
            )
            assert form.validate()
            assert not form.errors

def test_GetScoreData_invalid():
    with app.test_request_context('/'):
        with app.test_client() as client:
            response = client.get('/')
            csrf_token = extract_csrf_token(response.data.decode("utf-8"))

            form = GetScoreData(
                season = "winter",
                distance = "fifty",
                units = "metres",
                days_till = date.today(),
                is_comp = "True",
                csrf_token = csrf_token
            )
            assert not form.validate()
            assert form.errors   
        
def test_GetNewScore_empty():
    with app.test_request_context("/add_score"):
        form = GetNewScore()
        assert not form.validate()
        assert form.errors
        
def test_GetNewScore_valid():
    with app.test_request_context('/add_score'):
        with app.test_client() as client:
            response = client.get('/add_score')
            csrf_token = extract_csrf_token(response.data.decode("utf-8"))

            form = GetNewScore(
                season = "outdoors",
                arrow_average = 9.00,
                distance = 50,
                units = 1.09361,
                date = date.today(),
                golds = 36,
                total_arrows = 36,
                is_comp = 1,
                csrf_token = csrf_token
            )
            assert form.validate()
            assert not form.errors

def test_GetNewScore_invalid():
    with app.test_request_context('/add_score'):
        with app.test_client() as client:
            response = client.get('/add_score')
            csrf_token = extract_csrf_token(response.data.decode("utf-8"))

            form = GetNewScore(
                season = "winter",
                arrow_average = 9.00,
                distance = 50,
                units = 1.09361,
                date = date.today(),
                golds = 36,
                total_arrows = 36,
                is_comp = 1,
                csrf_token = csrf_token
            )
            assert not form.validate()
            assert form.errors   
            
def test_GetNewScore_value_out_of_range():
    with app.test_request_context('/add_score'):
        with app.test_client() as client:
            response = client.get('/add_score')
            csrf_token = extract_csrf_token(response.data.decode("utf-8"))

            form = GetNewScore(
                season = "outdoors",
                arrow_average = 11.00, # > 10
                distance = 50,
                units = 1.09361,
                date = date.today(),
                golds = 36,
                total_arrows = 36,
                is_comp = 1,
                csrf_token = csrf_token
            )
            assert not form.validate()
            assert form.errors
