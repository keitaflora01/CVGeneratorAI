import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import json
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
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

@csrf_exempt
def generate_document(request):
    """Generate CV or Letter of Motivation using Gemini and Tavily APIs"""
    logger.info(f"[generate_document] {time.strftime('%Y-%m-%d %H:%M:%S')} | Method: {request.method} | Path: {request.path} | Headers: {dict(request.headers)}")

    if request.method == 'POST':
        try:
            logger.debug(f"POST Data: {request.POST.dict()}")
            logger.debug(f"Files: {request.FILES}")

            target_role = request.POST.get('targetRole', '').strip()
            company = request.POST.get('company', '').strip()
            keywords = request.POST.get('keywords', '').strip()
            tone = request.POST.get('tone', 'professionnel')
            job_description = request.POST.get('jobDescription', '').strip()
            document_type = request.POST.get('documentType', 'CV')
            skills = [skill.strip() for skill in request.POST.get('skills', '').split(',') if skill.strip()]
            try:
                experiences = json.loads(request.POST.get('experiences', '[]'))
                education = json.loads(request.POST.get('education', '[]'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for experiences/education: {str(e)}")
                return render(request, 'user/generate.html', {
                    'error': 'Invalid format for experiences or education'
                })

            if not target_role or not job_description:
                logger.warning("Missing required fields: targetRole or jobDescription")
                return render(request, 'user/generate.html', {
                    'error': 'Target role and job description are required'
                })

            # Create document record
            user = request.user if request.user.is_authenticated else None
            logger.info(f"Creating document for user: {user.email if user else 'Anonymous'}")
            document = Document.objects.create(
                user=user,
                type=document_type,
                titre=f"{document_type} for {target_role}",
                poste=target_role,
                entreprise=company,
                statut='processing',
                metadata={
                    'keywords': keywords,
                    'tone': tone,
                    'job_description_preview': job_description[:100] + '...' if job_description else ''
                }
            )
            logger.info(f"Document created with ID: {document.id}")

            # Handle CV image
            if 'cv_image' in request.FILES and document_type == 'CV':
                cv_image = request.FILES['cv_image']
                logger.debug(f"CV image received: {cv_image.name}, size: {cv_image.size}")
                if cv_image.size > 2 * 1024 * 1024:
                    logger.warning(f"Image size exceeds 2MB: {cv_image.size}")
                    document.delete()
                    return render(request, 'user/generate.html', {
                        'error': 'Image must not exceed 2MB'
                    })
                CVImage.objects.create(
                    document=document,
                    image=cv_image,
                    description=f"Professional photo for {target_role}"
                )
                logger.info("CV image saved successfully")

            # Create processing steps
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

            # Prepare prompt based on document type
            user_data = {
                'name': user.full_name if user and user.is_authenticated and hasattr(user, 'full_name') and user.full_name else user.email if user and user.is_authenticated else 'Anonymous',
                'email': user.email if user and user.is_authenticated else 'N/A',
                'skills': skills,
                'experiences': experiences,
                'education': education
            }
            logger.debug(f"User data for prompt: {user_data}")
            prompt = _get_prompt(document_type, target_role, company, keywords, tone, job_description, user_data, context)
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
                    'error': f'Failed to generate document: {str(e)}'
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
                'error': f'An error occurred: {str(e)}'
            })

    elif request.method == 'GET':
        logger.info("Rendering generate.html for GET request")
        return render(request, 'user/generate.html')
    
    else:
        logger.warning(f"Method {request.method} not allowed for /agent/generate/")
        return HttpResponse(status=405, content="Method Not Allowed")

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

def _get_prompt(document_type, target_role, company, keywords, tone, job_description, user_data, context):
    """Generate prompt for CV or LM"""
    logger.debug(f"Generating prompt for {document_type}")
    if document_type == 'CV':
        prompt = f"""
        Generate a professional CV for a {target_role} position at {company}. 
        Use a {tone} tone. Incorporate the following details:
        - User: {user_data.get('name', 'Anonymous')}
        - Email: {user_data.get('email', 'N/A')}
        - Skills: {', '.join(user_data.get('skills', [])) + ', ' + keywords if keywords else ', '.join(user_data.get('skills', []))}
        - Experiences: {json.dumps(user_data.get('experiences', []))}
        - Education: {json.dumps(user_data.get('education', []))}
        - Job Description: {job_description}
        - Additional Context: {context}
        Format the CV in markdown with clear sections for Personal Information, Skills, Professional Experience, and Education. Ensure the content is tailored to the job description and company.
        """
    else:  # LM
        prompt = f"""
        Generate a professional Letter of Motivation for a {target_role} position at {company}. 
        Use a {tone} tone. Incorporate the following details:
        - User: {user_data.get('name', 'Anonymous')}
        - Email: {user_data.get('email', 'N/A')}
        - Skills: {', '.join(user_data.get('skills', [])) + ', ' + keywords if keywords else ', '.join(user_data.get('skills', []))}
        - Experiences: {json.dumps(user_data.get('experiences', []))}
        - Education: {json.dumps(user_data.get('education', []))}
        - Job Description: {job_description}
        - Additional Context: {context}
        Address the letter to the hiring manager at {company}. Highlight relevant skills and experiences, and explain why the candidate is a good fit for the role and company culture. Format the letter in markdown with a formal greeting, body (3-4 paragraphs), and closing.
        """
    logger.debug(f"Prompt generated: {prompt[:200]}...")
    return prompt

@login_required
def document_detail(request, document_id):
    """Display document details"""
    logger.info(f"Fetching document {document_id} for user {request.user.email}")
    document = get_object_or_404(Document, id=document_id, user=request.user)
    context = {
        'document': document,
        'etapes': document.etape_traitement_set.all().order_by('ordre')
    }
    if document.type == 'CV' and hasattr(document, 'cv_image'):
        context['cv_image'] = document.cv_image
        logger.debug(f"CV image found for document {document_id}")
    logger.info(f"Rendering document_detail for document {document_id}")
    return render(request, 'user/generate_document.html', context)

@login_required
def download_document(request, document_id):
    """Download generated document as PDF"""
    logger.info(f"Downloading document {document_id} for user {request.user.email}")
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if document.statut != 'completed':
        logger.warning(f"Document {document_id} not ready for download, status: {document.statut}")
        return JsonResponse({'error': 'Document not ready'})
    
    logger.debug(f"Generating PDF for document {document_id}")
    pdf_content = generate_pdf(document)
    
    filename = f"{document.type}_{document.poste.replace(' ', '_')}.pdf"
    content_type = 'application/pdf'
    
    response = HttpResponse(pdf_content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    logger.info(f"PDF generated for document {document_id}, filename: {filename}")
    return response

def generate_pdf(document):
    """Generate PDF from document content"""
    logger.debug(f"Starting PDF generation for document {document.id}")
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, document.titre)
    y = 750
    for line in document.contenu.split('\n'):
        if y < 50:
            c.showPage()
            y = 750
        c.drawString(100, y, line[:80])  # Truncate long lines
        y -= 15
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    logger.debug(f"PDF generated successfully for document {document.id}")
    return pdf

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