import os
import time
from datetime import datetime

import jwt
import pytest

from src.auth import create_token,decode_token

def test_token_identifies_the_user()-> None:
    claims = decode_token(create_token(7,a@))