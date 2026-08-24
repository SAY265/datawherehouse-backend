"""Recognizer plugins được đăng ký vào Presidio theo từng ngôn ngữ."""

from presidio_analyzer import EntityRecognizer

RecognizerCollection = tuple[EntityRecognizer, ...]

__all__ = ["RecognizerCollection"]
