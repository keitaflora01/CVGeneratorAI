from datetime import datetime
import logging
import os
from django.template.loader import render_to_string
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model
import json
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from docx import Document as DocxDocument
import markdown
from weasyprint import HTML
import google.generativeai as genai
from decouple import config, UndefinedValueError
from tavily import TavilyClient
from Agent.models import Document, EtapeTraitement, CVImage

# Configure logging
logger = logging.getLogger(__name__)

User = get_user_model()

# Configure API clients safely
try:
    GEMINI_API_KEY = config('GEMINI_API_KEY')
    TAVILY_API_KEY = config('TAVILY_API_KEY')
    genai.configure(api_key=GEMINI_API_KEY)
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
except UndefinedValueError as e:
    logger.error(f"Missing environment variable: {str(e)}")
    raise Exception(f"Missing environment variable: {str(e)}")

def get_available_templates():
    """Dynamically retrieve available CV and LM templates from directories."""
    templates = []
    base_dir = settings.TEMPLATES[0]['DIRS'][0]  # Assumes templates are in the first template directory

    # CV templates
    cv_template_dir = os.path.join(base_dir, 'cv-templates')
    if os.path.exists(cv_template_dir):
        for filename in os.listdir(cv_template_dir):
            if filename.endswith('.html'):
                template_id = filename.replace('.html', '')
                template_name = template_id.replace('-', ' ').title()
                templates.append({
                    'id': template_id,
                    'type': 'CV',
                    'name': template_name,
                    'path': os.path.join('cv-templates', filename)
                })

    # LM templates
    lm_template_dir = os.path.join(base_dir, 'lettres-motivation')
    if os.path.exists(lm_template_dir):
        for filename in os.listdir(lm_template_dir):
            if filename.endswith('.html'):
                template_id = filename.replace('.html', '')
                template_name = template_id.replace('-', ' ').title()
                templates.append({
                    'id': template_id,
                    'type': 'LM',
                    'name': template_name,
                    'path': os.path.join('lettres-motivation', filename)
                })

    logger.debug(f"Retrieved templates: {[t['name'] for t in templates]}")
    return templates

@csrf_exempt
def generate_document(request):
    """Generate CV or Letter of Motivation using Gemini and Tavily APIs"""
    logger.info(f"[generate_document] {time.strftime('%Y-%m-%d %H:%M:%S')} | Method: {request.method} | Path: {request.path} | Headers: {dict(request.headers)}")

    if request.method == 'POST':
        try:
            logger.debug(f"POST Data: {request.POST.dict()}")
            logger.debug(f"Files: {request.FILES}")

            # Extract form data
            target_role = request.POST.get('targetRole', '').strip()
            company = request.POST.get('company', '').strip()
            keywords = request.POST.get('keywords', '').strip()
            tone = request.POST.get('tone', 'professionnel')
            job_description = request.POST.get('jobDescription', '').strip()
            document_type = request.POST.get('documentType', 'CV')
            linkedin_url = request.POST.get('linkedin_url', '').strip()
            github_url = request.POST.get('github_url', '').strip()
            telephone = request.POST.get('telephone', '').strip()
            langue = request.POST.get('langue', 'fr')
            template_id = request.POST.get('template_id', 'template1-moderne-bleu')  # Default
            template_utilise = request.POST.get('template_utilise', 'Template1 Moderne Bleu')
            skills = [skill.strip() for skill in request.POST.get('skills', '').split(',') if skill.strip()]
            try:
                experiences = json.loads(request.POST.get('experiences', '[]'))
                education = json.loads(request.POST.get('education', '[]'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for experiences/education: {str(e)}")
                return render(request, 'user/generate.html', {
                    'error': 'Invalid format for experiences or education',
                    'templates': get_available_templates()
                })

            if not target_role or not job_description:
                logger.warning("Missing required fields: targetRole or jobDescription")
                return render(request, 'user/generate.html', {
                    'error': 'Target role and job description are required',
                    'templates': get_available_templates()
                })

            # Create or update document record
            user = request.user if request.user.is_authenticated else None
            logger.info(f"Creating document for user: {user.email if user else 'Anonymous'}")
            doc_id = request.POST.get('doc_id')
            if doc_id:
                document = get_object_or_404(Document, id=doc_id, user=user)
                document.type = document_type
                document.titre = f"{document_type} for {target_role}"
                document.poste = target_role
                document.entreprise = company
                document.linkedin_url = linkedin_url
                document.github_url = github_url
                document.telephone = telephone
                document.langue = langue
                document.template_utilise = template_utilise
                document.statut = 'processing'
                document.metadata = {
                    'keywords': keywords,
                    'tone': tone,
                    'job_description_preview': job_description[:100] + '...' if job_description else '',
                    'linkedin_url': linkedin_url,
                    'github_url': github_url,
                    'telephone': telephone,
                    'langue': langue,
                    'template_id': template_id,
                    'template_utilise': template_utilise
                }
            else:
                document = Document.objects.create(
                    user=user,
                    type=document_type,
                    titre=f"{document_type} for {target_role}",
                    poste=target_role,
                    entreprise=company,
                    linkedin_url=linkedin_url,
                    github_url=github_url,
                    telephone=telephone,
                    langue=langue,
                    template_utilise=template_utilise,
                    statut='processing',
                    metadata={
                        'keywords': keywords,
                        'tone': tone,
                        'job_description_preview': job_description[:100] + '...' if job_description else '',
                        'linkedin_url': linkedin_url,
                        'github_url': github_url,
                        'telephone': telephone,
                        'langue': langue,
                        'template_id': template_id,
                        'template_utilise': template_utilise
                    }
                )
            logger.info(f"Document {'updated' if doc_id else 'created'} with ID: {document.id}")

            # Handle CV image
            if 'cv_image' in request.FILES and document_type == 'CV':
                cv_image = request.FILES['cv_image']
                logger.debug(f"CV image received: {cv_image.name}, size: {cv_image.size}")
                if cv_image.size > 2 * 1024 * 1024:
                    logger.warning(f"Image size exceeds 2MB: {cv_image.size}")
                    document.delete()
                    return render(request, 'user/generate.html', {
                        'error': 'Image must not exceed 2MB',
                        'templates': get_available_templates()
                    })
                CVImage.objects.create(
                    document=document,
                    image=cv_image,
                    description=f"Professional photo for {target_role}"
                )
                logger.info("CV image saved successfully")

            # Create processing steps
            EtapeTraitement.objects.filter(document=document).delete()
            etapes_data = [
                {"nom": "Job offer analysis", "ordre": 1},
                {"nom": "Profile adaptation", "ordre": 2},
                {"nom": "Content generation", "ordre": 3},
                {"nom": "Optimization", "ordre": 4},
                {"nom": "Final validation", "ordre": 5},
            ]
            for etape_data in etapes_data:
                EtapeTraitement.objects.create(document=document, **etape_data)
            logger.debug("Processing steps created")

            # Fetch additional context using Tavily
            try:
                logger.info(f"Searching Tavily for: {target_role} job requirements {company}")
                tavily_response = tavily_client.search(
                    query=f"{target_role} job requirements {company}",
                    search_depth="basic",
                    max_results=3
                )
                context = "\n".join([result['content'] for result in tavily_response['results']])
                logger.debug(f"Tavily context: {context[:200]}...")
            except Exception as e:
                logger.error(f"Tavily API error: {str(e)}")
                context = "No additional context available."

            # Prepare prompt based on document type and template
            user_data = {
                'name': user.full_name if user and user.is_authenticated and hasattr(user, 'full_name') and user.full_name else user.full_name if user and user.is_authenticated else 'Anonymous',
                'email': user.email if user and user.is_authenticated else 'N/A',
                'linkedin_url': linkedin_url,
                'github_url': github_url,
                'telephone': telephone,
                'skills': skills,
                'experiences': experiences,
                'education': education
            }
            logger.debug(f"User data for prompt: {user_data}")
            prompt = _get_prompt(document_type, target_role, company, keywords, tone, job_description, user_data, context, langue, template_id)
            logger.debug(f"Generated prompt: {prompt[:200]}...")

            # Generate content using Gemini API
            try:
                logger.info("Calling Gemini API for content generation")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                generated_content = response.text
                logger.info("Content generated successfully")
            except Exception as e:
                logger.error(f"Gemini API error: {str(e)}")
                document.delete()
                return render(request, 'user/generate.html', {
                    'error': f'Failed to generate document: {str(e)}',
                    'templates': get_available_templates()
                })

            # Update document
            document.statut = 'completed'
            document.score = 85  # Placeholder score
            document.contenu = generated_content
            document.save()
            logger.info(f"Document {document.id} updated to completed, score: {document.score}")

            # Mark steps as completed
            for etape in document.etape_traitement_set.all():
                etape.statut = 'completed'
                etape.save()
            logger.debug("All processing steps marked as completed")

            logger.info(f"Redirecting to dashboard for document {document.id}")
            return redirect('comptes:dashboard')

        except Exception as e:
            logger.error(f"Error in generate_document: {str(e)}", exc_info=True)
            return render(request, 'user/generate.html', {
                'error': f'An error occurred: {str(e)}',
                'templates': get_available_templates()
            })

    elif request.method == 'GET':
        context = {'templates': get_available_templates()}
        doc_id = request.GET.get('doc_id')
        template_id = request.GET.get('template_id')
        if doc_id:
            document = get_object_or_404(Document, id=doc_id, user=request.user)
            context.update({
                'document': document,
                'targetRole': document.poste,
                'company': document.entreprise,
                'keywords': document.metadata.get('keywords', ''),
                'tone': document.metadata.get('tone', 'professionnel'),
                'jobDescription': document.metadata.get('job_description_preview', '')[:100],
                'documentType': document.type,
                'linkedin_url': document.linkedin_url,
                'github_url': document.github_url,
                'telephone': document.telephone,
                'langue': document.langue,
                'template_id': document.metadata.get('template_id', ''),
                'template_utilise': document.metadata.get('template_utilise', 'Template1 Moderne Bleu'),
                'skills': ', '.join(json.loads(document.metadata.get('skills', '[]'))),
                'experiences': json.loads(document.metadata.get('experiences', '[]')),
                'education': json.loads(document.metadata.get('education', '[]')),
            })
        if template_id:
            context['template_id'] = template_id
            context['template_utilise'] = next((t['name'] for t in get_available_templates() if t['id'] == template_id), 'Template1 Moderne Bleu')
        logger.info("Rendering generate.html for GET request")
        return render(request, 'user/generate.html', context)
    
    else:
        logger.warning(f"Method {request.method} not allowed for /agent/generate/")
        return HttpResponse(status=405, content="Method Not Allowed")

@csrf_exempt
@login_required
def delete_document(request, document_id):
    """API to delete a document"""
    logger.info(f"Deleting document {document_id} for user {request.user.email}")
    if request.method == 'DELETE':
        document = get_object_or_404(Document, id=document_id, user=request.user)
        try:
            document.delete()
            logger.info(f"Document {document_id} deleted successfully")
            return JsonResponse({'success': True, 'message': 'Document deleted'})
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    logger.warning(f"Method {request.method} not allowed for delete document")
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
def test_post_endpoint(request):
    """Debug endpoint to test POST requests"""
    logger.info(f"[test_post_endpoint] {time.strftime('%Y-%m-%d %H:%M:%S')} | Method: {request.method} | Path: {request.path} | Headers: {dict(request.headers)}")
    if request.method == 'POST':
        logger.debug(f"POST Data: {request.POST.dict()}")
        return JsonResponse({'success': True, 'message': 'POST request received', 'data': request.POST.dict()})
    elif request.method == 'GET':
        logger.info("GET request to test_post_endpoint")
        return JsonResponse({'success': True, 'message': 'GET request received'})
    else:
        logger.warning(f"Method {request.method} not allowed for test_post_endpoint")
        return HttpResponse(status=405, content="Method Not Allowed")

def _get_prompt(document_type, target_role, company, keywords, tone, job_description, user_data, context, langue, template_id):
    """Generate prompt for CV or LM with template-specific styling"""
    logger.debug(f"Generating prompt for {document_type} with template {template_id}")
    
    # Compute skills string outside f-string
    skills_list = user_data.get('skills', [])
    skills_string = ', '.join(skills_list)
    if keywords:
        skills_string = f"{skills_string}, {keywords}" if skills_string else keywords

    # Define template-specific styling instructions
    template_styles = {
        'template1-moderne-bleu': {
            'description': 'Modern design with a blue and purple gradient sidebar, white text on dark background, clean typography, and structured sections for Contact, Skills, Languages, Profile, Experience, and Education.',
            'formatting': 'For CV: Use plain text with sections marked by ## Profil, ## Compétences, ## Expérience Professionnelle, ## Formation, ## Projets. Use - for bullet points. For LM: Use a single narrative block with formal greeting and closing.'
        },
        'template2-elegant-vert': {
            'description': 'Elegant design with green accents, grid layout, rounded skill tags, and a centered header with green gradient.',
            'formatting': 'For CV: Use plain text with sections marked by ## Profil, ## Compétences, ## Expérience Professionnelle, ## Formation, ## Projets. Use - for bullet points. For LM: Use a single narrative block with formal greeting and closing.'
        },
        'template3-minimaliste': {
            'description': 'Minimalist design with red accents, clean lines, and a focus on simplicity with a grid layout.',
            'formatting': 'For CV: Use plain text with sections marked by ## Profil, ## Compétences, ## Expérience Professionnelle, ## Formation, ## Projets. Use - for bullet points. For LM: Use a single narrative block with formal greeting and closing.'
        },
        'template4-corporate': {
            'description': 'Corporate design with navy blue accents, formal layout, and clear section separation with background highlights.',
            'formatting': 'For CV: Use plain text with sections marked by ## Profil, ## Compétences, ## Expérience Professionnelle, ## Formation, ## Projets. Use - for bullet points. For LM: Use a single narrative block with formal greeting and closing.'
        },
        'template5-creatif': {
            'description': 'Creative design with pink and yellow gradients, bold typography, and a focus on innovative projects.',
            'formatting': 'For CV: Use plain text with sections marked by ## Profil, ## Compétences, ## Expérience Professionnelle, ## Formation, ## Projets. Use - for bullet points. For LM: Use a single narrative block with formal greeting and closing.'
        },
        'template5-tech-startup': {
            'description': 'Dynamic tech startup style with light blue and purple gradients, bold callouts, and a focus on metrics and vision.',
            'formatting': 'For CV: Use plain text with sections marked by ## Profil, ## Compétences, ## Expérience Professionnelle, ## Formation, ## Projets. Use - for bullet points. For LM: Use a single narrative block with formal greeting and closing.'
        },
        'template1-lettre-classique-elegante': {
            'description': 'Classic and elegant letter with blue borders, formal tone, and right-aligned contact details.',
            'formatting': 'For LM: Use a single narrative block with a formal greeting (e.g., Madame, Monsieur), 3-4 paragraphs, and a formal closing (e.g., salutations distinguées).'
        },
        'template2-moderne-pro': {
            'description': 'Modern professional letter with light blue and purple gradients, concise structure, and highlighted achievements.',
            'formatting': 'For LM: Use a single narrative block with a formal greeting, 3-4 paragraphs with bullet points for achievements, and a formal closing.'
        },
        'template3-corporate-minimaliste': {
            'description': 'Corporate minimalist letter with navy blue accents, clean layout, and focus on key achievements.',
            'formatting': 'For LM: Use a single narrative block with a formal greeting, 3-4 paragraphs with bullet points for achievements, and a formal closing.'
        },
        'template4-creatif-colore': {
            'description': 'Creative and colorful letter with pink and teal gradients, bold typography, and a conversational tone.',
            'formatting': 'For LM: Use a single narrative block with a conversational greeting, 3-4 paragraphs, and a friendly closing.'
        }
    }

    template_style = template_styles.get(template_id, template_styles['template1-moderne-bleu'])

    if document_type == 'CV':
        prompt = f"""
        Generate a professional CV in {langue} for a {target_role} position at {company}. 
        Use a {tone} tone and the '{template_style['description']}' template style. Incorporate:
        - Name: {user_data.get('name', 'Anonymous')}
        - Email: {user_data.get('email', 'N/A')}
        - LinkedIn: {user_data.get('linkedin_url', 'N/A')}
        - GitHub: {user_data.get('github_url', 'N/A')}
        - Telephone: {user_data.get('telephone', 'N/A')}
        - Skills: {skills_string}
        - Experiences: {json.dumps(user_data.get('experiences', []))}
        - Education: {json.dumps(user_data.get('education', []))}
        - Job Description: {job_description}
        - Additional Context: {context}
        Format the CV as plain text with the following sections marked by headers:
        - ## Profil: A concise summary (150-200 words) tailored to {company} and {target_role}.
        - ## Compétences: A bulleted list of relevant skills using - for bullets.
        - ## Expérience Professionnelle: Detailed experiences with quantifiable achievements (e.g., 'Reduced deployment time by 20%').
        - ## Formation: Academic qualifications.
        - ## Projets: Relevant projects with GitHub links.
        Follow the '{template_style['formatting']}' style. Ensure content is tailored to {company}, emphasizing relevant skills and achievements.
        """
    else:  # LM
        prompt = f"""
        Generate a professional Letter of Motivation in {langue} for a {target_role} position at {company}. 
        Use a {tone} tone and the '{template_style['description']}' template style. Incorporate:
        - Name: {user_data.get('name', 'Anonymous')}
        - Email: {user_data.get('email', 'N/A')}
        - LinkedIn: {user_data.get('linkedin_url', 'N/A')}
        - GitHub: {user_data.get('github_url', 'N/A')}
        - Telephone: {user_data.get('telephone', 'N/A')}
        - Skills: {skills_string}
        - Experiences: {json.dumps(user_data.get('experiences', []))}
        - Education: {json.dumps(user_data.get('education', []))}
        - Job Description: {job_description}
        - Additional Context: {context}
        Format as a single narrative block with:
        - A formal greeting (e.g., Madame, Monsieur).
        - 3-4 paragraphs explaining why the candidate is a good fit for {company} and {target_role}, highlighting relevant skills and quantifiable achievements.
        - A formal closing (e.g., salutations distinguées) with contact information.
        Follow the '{template_style['formatting']}' style.
        """
    logger.debug(f"Prompt generated: {prompt[:200]}...")
    return prompt


def document_detail(request, document_id):
    """Display document details"""
    logger.info(f"Fetching document {document_id} for user {request.user.email}")
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Prepare context
    context = {
        'document': document,
        'etapes': document.etape_traitement_set.all().order_by('ordre')
    }
    
    # Parse content for CVs
    if document.type == 'CV':
        content = document.contenu
        profile_match = re.search(r'## Profil\s*(.*?)(##|$)', content, re.DOTALL)
        skills_match = re.search(r'## Compétences\s*(.*?)(##|$)', content, re.DOTALL)
        experience_match = re.search(r'## Expérience Professionnelle\s*(.*?)(##|$)', content, re.DOTALL)
        education_match = re.search(r'## Formation\s*(.*?)(##|$)', content, re.DOTALL)
        projects_match = re.search(r'## Projets\s*(.*?)(##|$)', content, re.DOTALL)
        
        # Process each section's lines to identify bullet points
        def process_lines(lines):
            return [{'text': line.strip(), 'is_bullet': line.strip().startswith('- ')} for line in lines if line.strip()]
        
        context['content_sections'] = {
            'profile': {
                'title': 'Profil',
                'content': process_lines(profile_match.group(1).strip().splitlines() if profile_match else ['No profile provided.'])
            },
            'skills': {
                'title': 'Compétences',
                'content': process_lines(skills_match.group(1).strip().splitlines() if skills_match else [])
            },
            'experience': {
                'title': 'Expérience Professionnelle',
                'content': process_lines(experience_match.group(1).strip().splitlines() if experience_match else [])
            },
            'education': {
                'title': 'Formation',
                'content': process_lines(education_match.group(1).strip().splitlines() if education_match else [])
            },
            'projects': {
                'title': 'Projets',
                'content': process_lines(projects_match.group(1).strip().splitlines() if projects_match else [])
            }
        }
    else:
        context['content_sections'] = {
            'letter': {
                'title': 'Lettre de Motivation',
                'content': [{'text': line.strip(), 'is_bullet': False} for line in document.contenu.splitlines() if line.strip()]
            }
        }
    
    # Include CV image if applicable
    if document.type == 'CV' and hasattr(document, 'cv_image'):
        context['cv_image'] = document.cv_image
        logger.debug(f"CV image found for document {document_id}")
    
    logger.info(f"Rendering document_detail for document {document_id}")
    return render(request, 'user/generate_document.html', context)
    
@login_required
def downlaod_document(request, document_id):
    """Download generated document in selected format"""
    logger.info(f"Downloading document {document_id} for user {request.user.email}")
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if document.statut != 'completed':
        logger.warning(f"Document {document_id} not ready for download, status: {document.statut}")
        return JsonResponse({'error': 'Document not ready'})
    
    export_format = request.GET.get('format', 'pdf')
    logger.debug(f"Generating document {document_id} in {export_format} format")
    
    filename = f"{document.type}_{document.poste.replace(' ', '_')}"
    
    # Prepare context for templates
    context = {
        'name': request.user.full_name if hasattr(request.user, 'full_name') and request.user.full_name else 'Anonymous',
        'email': request.user.email if request.user.is_authenticated else 'N/A',
        'telephone': document.telephone,
        'github_url': document.github_url,
        'github_username': document.github_url.split('/')[-1] if document.github_url else '',
        'linkedin_url': document.linkedin_url,
        'linkedin_username': document.linkedin_url.split('/')[-1] if document.linkedin_url else '',
        'target_role': document.poste,
        'company': document.entreprise,
        'company_address': document.entreprise or 'Unknown Address',
        'today': datetime.now().strftime('%d/%m/%Y'),
        'document': document,
    }

    # Parse AI-generated content (plain text with ## headers for CVs)
    content = document.contenu
    if document.type == 'CV':
        profile_match = re.search(r'## Profil\s*(.*?)(##|$)', content, re.DOTALL)
        skills_match = re.search(r'## Compétences\s*(.*?)(##|$)', content, re.DOTALL)
        experience_match = re.search(r'## Expérience Professionnelle\s*(.*?)(##|$)', content, re.DOTALL)
        education_match = re.search(r'## Formation\s*(.*?)(##|$)', content, re.DOTALL)
        projects_match = re.search(r'## Projets\s*(.*?)(##|$)', content, re.DOTALL)

        context['profile'] = profile_match.group(1).strip() if profile_match else 'No profile provided.'
        context['skills'] = skills_match.group(1).strip() if skills_match else ''
        context['experience'] = experience_match.group(1).strip() if experience_match else ''
        context['education'] = education_match.group(1).strip() if education_match else ''
        context['projects'] = projects_match.group(1).strip() if projects_match else ''
    else:
        context['letter_content'] = content

    # Handle CV image
    if document.type == 'CV' and hasattr(document, 'cv_image'):
        context['cv_image'] = document.cv_image.image.url
    else:
        context['cv_image'] = ''

    # Get template path
    templates = get_available_templates()
    template_id = document.metadata.get('template_id', 'template1-moderne-bleu' if document.type == 'CV' else 'template1-lettre-classique-elegante')
    template = next((t for t in templates if t['id'] == template_id and t['type'] == ('CV' if document.type == 'CV' else 'LM')), None)
    if not template:
        logger.error(f"Template {template_id} not found for document {document_id}")
        return JsonResponse({'error': 'Template not found'})
    template_path = template['path']

    if export_format == 'pdf':
        try:
            html_content = render_to_string(template_path, context)
            html = HTML(string=html_content, base_url=request.build_absolute_uri('/'))
            pdf_content = html.write_pdf()
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            logger.info(f"PDF generated for document {document_id}, filename: {filename}.pdf")
            return response
        except Exception as e:
            logger.error(f"WeasyPrint error for document {document_id}: {str(e)}")
            return JsonResponse({'error': f'PDF generation failed: {str(e)}'})
    elif export_format == 'docx':
        docx_content = generate_docx(document)
        response = HttpResponse(docx_content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}.docx"'
        logger.info(f"Word document generated for document {document_id}, filename: {filename}.docx")
        return response
    elif export_format == 'txt':
        txt_content = document.contenu.encode('utf-8')
        response = HttpResponse(txt_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}.txt"'
        logger.info(f"TXT document generated for document {document_id}, filename: {filename}.txt")
        return response
    elif export_format in ['png', 'jpg']:
        html_content = render_to_string(template_path, context)
        buffer = BytesIO()
        HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_png(buffer) if export_format == 'png' else HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_jpg(buffer)
        image_content = buffer.getvalue()
        buffer.close()
        content_type = 'image/png' if export_format == 'png' else 'image/jpeg'
        response = HttpResponse(image_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}.{export_format}"'
        logger.info(f"Image ({export_format}) generated for document {document_id}, filename: {filename}.{export_format}")
        return response
    else:
        logger.warning(f"Invalid export format: {export_format}")
        return JsonResponse({'error': 'Invalid export format'})

def generate_pdf(document):
    """Generate PDF from document content using ReportLab"""
    logger.debug(f"Starting PDF generation for document {document.id}")
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, document.titre)
    y = 720

    # Add content (markdown rendered as plain text)
    c.setFont("Helvetica", 12)
    for line in document.contenu.split('\n'):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
        c.drawString(100, y, line[:80])  # Truncate long lines
        y -= 15

    # Add image if available (for CV)
    if document.type == 'CV' and hasattr(document, 'cv_image') and document.cv_image.image:
        try:
            c.drawImage(document.cv_image.image.path, 400, 650, width=100, height=100)
        except Exception as e:
            logger.error(f"Error adding image to PDF for document {document.id}: {str(e)}")

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    logger.debug(f"PDF generated successfully for document {document.id}")
    return pdf

def generate_docx(document):
    """Generate Word document from document content"""
    logger.debug(f"Starting Word document generation for document {document.id}")
    doc = DocxDocument()
    doc.add_heading(document.titre, 0)
    for line in document.contenu.split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    docx = buffer.getvalue()
    buffer.close()
    logger.debug(f"Word document generated successfully for document {document.id}")
    return docx

@csrf_exempt
@login_required
def upload_cv_image(request, document_id):
    """API to upload CV image"""
    logger.info(f"Uploading CV image for document {document_id} by user {request.user.email}")
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        if document.type != 'CV':
            logger.warning(f"Document {document_id} is not a CV, image upload rejected")
            return JsonResponse({'success': False, 'error': 'Document must be a CV'})
        
        if 'image' not in request.FILES:
            logger.warning("No image provided in upload request")
            return JsonResponse({'success': False, 'error': 'No image provided'})
        
        image_file = request.FILES['image']
        logger.debug(f"Image file: {image_file.name}, size: {image_file.size}")
        cv_image, created = CVImage.objects.get_or_create(document=document)
        cv_image.image = image_file
        cv_image.description = f"Professional photo for {document.poste}"
        cv_image.save()
        
        logger.info(f"Image uploaded successfully for document {document_id}")
        return JsonResponse({
            'success': True,
            'message': 'Image uploaded successfully',
            'image_url': cv_image.image.url
        })
    
    logger.warning(f"Method {request.method} not allowed for image upload")
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def update_document_status(request, document_id):
    """API to update document status"""
    logger.info(f"Updating status for document {document_id} by user {request.user.email}")
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id, user=request.user)
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            score = data.get('score', 0)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in update_document_status: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        
        if new_status in dict(Document.STATUS_CHOICES).keys():
            document.statut = new_status
            document.score = score
            document.save()
            logger.info(f"Document {document_id} status updated to {new_status}, score: {score}")
            return JsonResponse({'success': True})
        
        logger.warning(f"Invalid status {new_status} for document {document_id}")
        return JsonResponse({'success': False, 'error': 'Invalid status'})
    
    logger.warning(f"Method {request.method} not allowed for status update")
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@login_required
def template_selection(request):
    """Display available templates for CV and LM"""
    logger.info(f"Fetching templates for user {request.user.email}")
    document_type = request.GET.get('document_type', 'CV')
    templates = [t for t in get_available_templates() if t['type'] == document_type]
    context = {
        'templates': templates,
        'document_type': document_type
    }
    return render(request, 'user/template_selection.html', context)