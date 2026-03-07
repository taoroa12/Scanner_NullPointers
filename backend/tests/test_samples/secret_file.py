# tests/test_samples/secret_file.py
# Этот файл содержит секреты - тест должен их найти

import os

# AWS ключи
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"  # должен найтись
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# GitHub токены
GITHUB_TOKEN = "ghp_123456789012345678901234567890123456"  # должен найтись

# API ключи
STRIPE_KEY = "sk_live_123456789012345678901234"  # должен найтись
GOOGLE_KEY = "AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz"

# JWT токен
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # должен найтись

# Пароль
DB_PASSWORD = "Postgres123!@#"  # должен найтись

# Это не секрет - обычный текст
normal_text = "Hello world, this is just a regular string"