#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gna_insights.settings')
django.setup()

from core.nlp_agent import NLPAgent

agent = NLPAgent()
result = agent.process_query('what is the weather today')
print('Response:', repr(result['response']))
print('Lowercase:', repr(result['response'].lower()))
print('Contains "I don\'t understand":', "I don't understand" in result['response'].lower())
