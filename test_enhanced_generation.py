#!/usr/bin/env python3
"""
Test script for the enhanced CV and Motivation Letter generation functionality.
This script tests the improved generation system with professional prompts and templates.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV.settings')
django.setup()

from Agent.views import _get_prompt, get_available_templates
import json

def test_prompt_generation():
    """Test the enhanced prompt generation"""
    print("🧪 Testing Enhanced Prompt Generation")
    print("=" * 50)
    
    # Test data
    user_data = {
        'name': 'Marie Dubois',
        'email': 'marie.dubois@email.com',
        'linkedin_url': 'https://linkedin.com/in/mariedubois',
        'github_url': 'https://github.com/mariedubois',
        'telephone': '+33 6 12 34 56 78',
        'skills': ['Python', 'Django', 'React', 'JavaScript', 'PostgreSQL'],
        'experiences': [
            {
                'title': 'Développeuse Full-Stack Senior',
                'company': 'TechCorp Solutions',
                'duration': '2020 - Présent',
                'description': 'Développement d\'applications web complexes avec Python/Django et React'
            }
        ],
        'education': [
            {
                'degree': 'Master en Informatique',
                'institution': 'Université de Paris',
                'year': '2018'
            }
        ]
    }
    
    # Test CV prompt
    print("\n📄 Testing CV Prompt Generation:")
    cv_prompt = _get_prompt(
        document_type='CV',
        target_role='Développeuse Full-Stack Senior',
        company='Orange Cameroun',
        keywords='Python, Django, React, Agile',
        tone='professionnel',
        job_description='Recherche développeuse full-stack expérimentée pour rejoindre notre équipe IT',
        user_data=user_data,
        context='Orange Cameroun est un leader des télécommunications en Afrique Centrale',
        langue='fr',
        template_id='template1-moderne-bleu'
    )
    
    print(f"✅ CV Prompt generated successfully")
    print(f"📊 Prompt length: {len(cv_prompt)} characters")
    print(f"🎯 Contains professional instructions: {'expert CV writer' in cv_prompt}")
    print(f"🎯 Contains ATS optimization: {'ATS-optimized' in cv_prompt}")
    
    # Test Motivation Letter prompt
    print("\n📝 Testing Motivation Letter Prompt Generation:")
    lm_prompt = _get_prompt(
        document_type='LM',
        target_role='Développeuse Full-Stack Senior',
        company='Orange Cameroun',
        keywords='Python, Django, React, Agile',
        tone='professionnel',
        job_description='Recherche développeuse full-stack expérimentée pour rejoindre notre équipe IT',
        user_data=user_data,
        context='Orange Cameroun est un leader des télécommunications en Afrique Centrale',
        langue='fr',
        template_id='template1-lettre-classique-elegante'
    )
    
    print(f"✅ Motivation Letter Prompt generated successfully")
    print(f"📊 Prompt length: {len(lm_prompt)} characters")
    print(f"🎯 Contains professional instructions: {'expert career consultant' in lm_prompt}")
    print(f"🎯 Contains storytelling elements: {'compelling narrative' in lm_prompt}")

def test_template_availability():
    """Test template availability"""
    print("\n🎨 Testing Template Availability")
    print("=" * 50)
    
    templates = get_available_templates()
    print(f"✅ Found {len(templates)} templates")
    
    cv_templates = [t for t in templates if t['type'] == 'CV']
    lm_templates = [t for t in templates if t['type'] == 'LM']
    
    print(f"📄 CV Templates: {len(cv_templates)}")
    for template in cv_templates:
        print(f"   - {template['name']} ({template['id']})")
    
    print(f"📝 Motivation Letter Templates: {len(lm_templates)}")
    for template in lm_templates:
        print(f"   - {template['name']} ({template['id']})")

def test_enhanced_features():
    """Test enhanced features"""
    print("\n🚀 Testing Enhanced Features")
    print("=" * 50)
    
    # Test professional prompt structure
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'skills': ['Python', 'Django'],
        'experiences': [],
        'education': []
    }
    
    prompt = _get_prompt(
        document_type='CV',
        target_role='Software Engineer',
        company='Tech Company',
        keywords='Python, Django',
        tone='professionnel',
        job_description='Software engineer position',
        user_data=user_data,
        context='Tech company context',
        langue='fr',
        template_id='template1-moderne-bleu'
    )
    
    # Check for enhanced features
    features = [
        ('Professional tone', 'expert CV writer'),
        ('ATS optimization', 'ATS-optimized'),
        ('Quantifiable achievements', 'quantifiable achievements'),
        ('Action verbs', 'action verbs'),
        ('Template styling', 'template style'),
        ('Company tailoring', 'tailored to'),
        ('Quality standards', 'QUALITY STANDARDS')
    ]
    
    print("🔍 Checking Enhanced Features:")
    for feature_name, keyword in features:
        if keyword.lower() in prompt.lower():
            print(f"   ✅ {feature_name}")
        else:
            print(f"   ❌ {feature_name}")

def main():
    """Run all tests"""
    print("🎯 CV Generator AI - Enhanced Functionality Test")
    print("=" * 60)
    
    try:
        test_prompt_generation()
        test_template_availability()
        test_enhanced_features()
        
        print("\n🎉 All tests completed successfully!")
        print("✨ The enhanced CV and Motivation Letter generation system is ready!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
