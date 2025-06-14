#!/usr/bin/env python
"""
AI Image Recognition System for Books4Geeks
Provides computer vision capabilities for book management:
- Book cover recognition and information extraction
- Automatic categorization based on visual analysis
- Damage detection for quality control
- Smart inventory counting through image processing
"""

import os
import cv2
import numpy as np
import base64
import json
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import logging
from typing import Dict, List, Tuple, Optional
import datetime
from dataclasses import dataclass

# Optional imports with fallbacks
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Configure logging
logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not available. OCR functionality will be limited.")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available. AI analysis will be limited.")

@dataclass
class BookInfo:
    """Data class for extracted book information"""
    title: str = ""
    authors: List[str] = None
    isbn: str = ""
    publisher: str = ""
    genre: str = ""
    description: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.authors is None:
            self.authors = []

@dataclass
class DamageAssessment:
    """Data class for book damage assessment"""
    is_damaged: bool = False
    damage_type: List[str] = None
    severity: str = "none"  # none, minor, moderate, severe
    confidence: float = 0.0
    affected_areas: List[str] = None
    
    def __post_init__(self):
        if self.damage_type is None:
            self.damage_type = []
        if self.affected_areas is None:
            self.affected_areas = []

class AIImageRecognition:
    """
    AI-powered image recognition system for book management
    Integrates with Google Gemini API for advanced computer vision
    """
    
    def __init__(self):
        """Initialize the AI Image Recognition system"""        # Configure Gemini API
        if GEMINI_AVAILABLE and hasattr(settings, 'GEMINI_API_KEY'):
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            if not GEMINI_AVAILABLE:
                logger.warning("Google Generative AI not available")
            else:
                logger.warning("Gemini API key not configured")
          # Initialize OCR reader
        try:
            if EASYOCR_AVAILABLE:
                self.ocr_reader = easyocr.Reader(['en'])
            else:
                self.ocr_reader = None
                logger.warning("EasyOCR not available, OCR functionality disabled")
        except Exception as e:
            logger.error(f"Failed to initialize OCR reader: {e}")
            self.ocr_reader = None
        
        # Book categories mapping
        self.genre_keywords = {
            'Fiction': ['novel', 'fiction', 'story', 'romance', 'mystery', 'thriller', 'fantasy', 'sci-fi'],
            'Non-Fiction': ['guide', 'manual', 'how-to', 'biography', 'history', 'politics', 'science'],
            'Programming': ['python', 'javascript', 'java', 'coding', 'programming', 'software', 'development'],
            'Business': ['business', 'management', 'marketing', 'finance', 'entrepreneur', 'leadership'],
            'Education': ['textbook', 'study', 'learning', 'education', 'academic', 'course'],
            'Technology': ['technology', 'tech', 'computer', 'digital', 'AI', 'machine learning'],
            'Self-Help': ['self-help', 'motivation', 'improvement', 'success', 'productivity']
        }

    def process_book_cover(self, image_path: str) -> Dict:
        """
        Main function to process book cover and extract all information
        
        Args:
            image_path: Path to the book cover image
            
        Returns:
            Dict containing all extracted information
        """
        try:
            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                return self._error_response("Failed to load image")
            
            # Extract book information
            book_info = self._extract_book_info(image)
            
            # Assess damage
            damage_assessment = self._assess_damage(image)
            
            # Auto-categorize
            category = self._auto_categorize(book_info, image)
            
            return {
                'success': True,
                'book_info': {
                    'title': book_info.title,
                    'authors': book_info.authors,
                    'isbn': book_info.isbn,
                    'publisher': book_info.publisher,
                    'genre': book_info.genre,
                    'description': book_info.description,
                    'confidence': book_info.confidence
                },
                'damage_assessment': {
                    'is_damaged': damage_assessment.is_damaged,
                    'damage_type': damage_assessment.damage_type,
                    'severity': damage_assessment.severity,
                    'confidence': damage_assessment.confidence,
                    'affected_areas': damage_assessment.affected_areas
                },
                'suggested_category': category,
                'processing_timestamp': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing book cover: {e}")
            return self._error_response(str(e))

    def _load_and_preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load and preprocess image for analysis"""
        try:
            # Load image
            if image_path.startswith('http'):
                response = requests.get(image_path)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image quality
            image = self._enhance_image(image)
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None

    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better recognition"""
        try:
            # Adjust contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Adjust sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)
            
            # Adjust brightness
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image

    def _extract_book_info(self, image: np.ndarray) -> BookInfo:
        """Extract book information using OCR and AI"""
        book_info = BookInfo()
        
        try:
            # Extract text using OCR
            ocr_text = self._extract_text_ocr(image)
            
            # Use AI to analyze the image and extracted text
            if self.model:
                ai_analysis = self._analyze_with_ai(image, ocr_text)
                book_info = self._parse_ai_response(ai_analysis)
            else:
                # Fallback: basic text processing
                book_info = self._basic_text_analysis(ocr_text)
                
        except Exception as e:            logger.error(f"Error extracting book info: {e}")
            
        return book_info

    def _extract_text_ocr(self, image: np.ndarray) -> str:
        """Extract text from image using OCR"""
        extracted_text = ""
        
        # Try EasyOCR first if available
        if self.ocr_reader:
            try:
                # Convert BGR to RGB for EasyOCR
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Extract text
                results = self.ocr_reader.readtext(rgb_image)
                
                # Combine all text
                extracted_text = " ".join([result[1] for result in results])
                logger.info(f"EasyOCR extracted text: {extracted_text[:100]}...")
                
            except Exception as e:
                logger.error(f"EasyOCR extraction error: {e}")
        
        # Fallback to OpenCV-based text detection if EasyOCR failed or unavailable
        if not extracted_text:
            try:
                extracted_text = self._opencv_text_extraction(image)
                logger.info(f"OpenCV extracted text regions: {len(extracted_text.split())} words")
            except Exception as e:
                logger.error(f"OpenCV text extraction error: {e}")
        
        return extracted_text

    def _opencv_text_extraction(self, image: np.ndarray) -> str:
        """Extract text regions using OpenCV text detection (fallback method)"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding for better text detection
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Find contours that might be text
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that look like text regions
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                area = cv2.contourArea(contour)
                
                # Text regions typically have certain aspect ratios and sizes
                if 0.2 < aspect_ratio < 10 and 100 < area < 10000:
                    text_regions.append((x, y, w, h))
            
            # Sort text regions by position (top to bottom, left to right)
            text_regions.sort(key=lambda r: (r[1], r[0]))
            
            # For now, we'll return information about detected text regions
            # In a full implementation, this would be passed to an OCR engine
            extracted_info = []
            for i, (x, y, w, h) in enumerate(text_regions[:10]):  # Limit to top 10 regions
                # Extract the region
                region = gray[y:y+h, x:x+w]
                
                # Simple heuristic: larger regions are likely titles, smaller ones are details
                if w * h > 2000:
                    extracted_info.append(f"TITLE_REGION_{i}")
                elif w * h > 500:
                    extracted_info.append(f"TEXT_REGION_{i}")
            
            # Return a placeholder that indicates text regions were found
            return f"Text regions detected: {len(text_regions)} areas"
            
        except Exception as e:
            logger.error(f"OpenCV text extraction error: {e}")
            return ""

    def _analyze_with_ai(self, image: np.ndarray, ocr_text: str) -> str:
        """Use Gemini AI to analyze book cover"""
        try:
            # Convert image to base64
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            prompt = f"""
            Analyze this book cover image and the OCR extracted text: "{ocr_text}"
            
            Please provide a JSON response with the following information:
            {{
                "title": "book title",
                "authors": ["author1", "author2"],
                "publisher": "publisher name",
                "genre": "book genre/category",
                "isbn": "ISBN if visible",
                "description": "brief description based on cover",
                "confidence": 0.95
            }}
            
            Rules:
            - Extract the main title prominently displayed
            - Identify author names (usually below or above title)
            - Determine genre from visual elements, imagery, and text style
            - Look for ISBN numbers (usually 13 digits)
            - Publisher info often at bottom of cover
            - Confidence should be 0.0-1.0 based on clarity
            - Return valid JSON only
            """
            
            # Generate content with image
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64
                }
            ])
            
            return response.text
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return "{}"

    def _parse_ai_response(self, ai_response: str) -> BookInfo:
        """Parse AI response into BookInfo object"""
        book_info = BookInfo()
        
        try:
            # Clean the response (remove markdown if present)
            clean_response = ai_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            
            # Parse JSON
            data = json.loads(clean_response)
            
            book_info.title = data.get('title', '')
            book_info.authors = data.get('authors', [])
            book_info.publisher = data.get('publisher', '')
            book_info.genre = data.get('genre', '')
            book_info.isbn = data.get('isbn', '')
            book_info.description = data.get('description', '')
            book_info.confidence = float(data.get('confidence', 0.0))
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            
        return book_info

    def _basic_text_analysis(self, text: str) -> BookInfo:
        """Basic text analysis when AI is not available"""
        book_info = BookInfo()
        
        try:
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Simple heuristics
            if lines:
                # Assume first significant line is title
                book_info.title = lines[0]
                
                # Look for author patterns
                for line in lines:
                    if any(word in line.lower() for word in ['by', 'author']):
                        book_info.authors = [line.replace('by', '').replace('author', '').strip()]
                        break
                
                # Basic genre detection
                text_lower = text.lower()
                for genre, keywords in self.genre_keywords.items():
                    if any(keyword in text_lower for keyword in keywords):
                        book_info.genre = genre
                        break
                
            book_info.confidence = 0.5  # Lower confidence for basic analysis
            
        except Exception as e:
            logger.error(f"Basic text analysis error: {e}")
            
        return book_info

    def _assess_damage(self, image: np.ndarray) -> DamageAssessment:
        """Assess book damage using computer vision"""
        damage = DamageAssessment()
        
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edge quality (damaged books have broken edges)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Detect color consistency (fading, stains)
            color_std = np.std(image)
            
            # Detect scratches and tears using morphological operations
            kernel = np.ones((3,3), np.uint8)
            opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            damage_mask = cv2.absdiff(gray, opened)
            damage_ratio = np.sum(damage_mask > 30) / damage_mask.size
            
            # Analysis with AI if available
            if self.model:
                ai_damage = self._analyze_damage_with_ai(image)
                damage = self._combine_damage_analysis(damage, ai_damage)
            else:
                # Basic damage assessment
                damage.confidence = 0.6
                
                if edge_density < 0.1 or color_std > 80 or damage_ratio > 0.05:
                    damage.is_damaged = True
                    
                    if damage_ratio > 0.1:
                        damage.severity = "severe"
                        damage.damage_type = ["tears", "major_wear"]
                    elif color_std > 100:
                        damage.severity = "moderate"
                        damage.damage_type = ["fading", "stains"]
                    else:
                        damage.severity = "minor"
                        damage.damage_type = ["minor_wear"]
                        
        except Exception as e:
            logger.error(f"Damage assessment error: {e}")
            
        return damage

    def _analyze_damage_with_ai(self, image: np.ndarray) -> Dict:
        """Use AI to analyze book damage"""
        try:
            # Convert image to base64
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            prompt = """
            Analyze this book cover for any damage or wear. Look for:
            - Tears, rips, or holes
            - Fading or discoloration
            - Stains or marks
            - Bent or crumpled areas
            - Scratches or scuffs
            - Overall condition
            
            Provide a JSON response:
            {
                "is_damaged": true/false,
                "damage_types": ["tear", "stain", "fade", "bend", "scratch"],
                "severity": "none/minor/moderate/severe",
                "affected_areas": ["corner", "edge", "center", "spine"],
                "confidence": 0.95
            }
            """
            
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64
                }
            ])
            
            return json.loads(response.text.strip())
            
        except Exception as e:
            logger.error(f"AI damage analysis error: {e}")
            return {}

    def _combine_damage_analysis(self, basic_damage: DamageAssessment, ai_damage: Dict) -> DamageAssessment:
        """Combine basic and AI damage analysis"""
        try:
            if ai_damage:
                basic_damage.is_damaged = ai_damage.get('is_damaged', basic_damage.is_damaged)
                basic_damage.damage_type = ai_damage.get('damage_types', basic_damage.damage_type)
                basic_damage.severity = ai_damage.get('severity', basic_damage.severity)
                basic_damage.affected_areas = ai_damage.get('affected_areas', basic_damage.affected_areas)
                basic_damage.confidence = max(basic_damage.confidence, ai_damage.get('confidence', 0.0))
                
        except Exception as e:
            logger.error(f"Error combining damage analysis: {e}")
            
        return basic_damage

    def _auto_categorize(self, book_info: BookInfo, image: np.ndarray) -> str:
        """Automatically categorize book based on extracted information"""
        try:
            # Primary: Use extracted genre
            if book_info.genre:
                return book_info.genre
            
            # Secondary: Analyze title and description
            text_content = f"{book_info.title} {book_info.description}".lower()
            
            for category, keywords in self.genre_keywords.items():
                if any(keyword in text_content for keyword in keywords):
                    return category
            
            # Tertiary: Visual analysis with AI
            if self.model:
                category = self._visual_categorization(image)
                if category:
                    return category
                    
            return "General"
            
        except Exception as e:
            logger.error(f"Auto-categorization error: {e}")
            return "General"

    def _visual_categorization(self, image: np.ndarray) -> str:
        """Use AI for visual categorization"""
        try:
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            prompt = """
            Based on the visual elements of this book cover (colors, imagery, typography, design style), 
            what category would this book likely belong to?
            
            Options: Fiction, Non-Fiction, Programming, Business, Education, Technology, Self-Help, General
            
            Respond with just the category name.
            """
            
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg", 
                    "data": image_base64
                }
            ])
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Visual categorization error: {e}")
            return ""

    def count_books_in_image(self, image_path: str) -> Dict:
        """Count books in a shelf/inventory image"""
        try:
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                return self._error_response("Failed to load image")
            
            # Detect book spines using computer vision
            book_count = self._detect_book_spines(image)
            
            # Use AI for verification if available
            if self.model:
                ai_count = self._ai_count_books(image)
                # Take average of both methods
                final_count = int((book_count + ai_count) / 2)
            else:
                final_count = book_count
            
            return {
                'success': True,
                'book_count': final_count,
                'detection_method': 'hybrid' if self.model else 'computer_vision',
                'confidence': 0.8 if self.model else 0.6,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Book counting error: {e}")
            return self._error_response(str(e))

    def _detect_book_spines(self, image: np.ndarray) -> int:
        """Detect book spines using computer vision techniques"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that look like book spines
            book_contours = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = h / w if w > 0 else 0
                area = cv2.contourArea(contour)
                
                # Book spines are typically tall and narrow
                if 2 < aspect_ratio < 10 and area > 500:
                    book_contours.append(contour)
            
            return len(book_contours)
            
        except Exception as e:
            logger.error(f"Book spine detection error: {e}")
            return 0

    def _ai_count_books(self, image: np.ndarray) -> int:
        """Use AI to count books in image"""
        try:
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            prompt = """
            Count the number of books visible in this image. 
            Look for book spines, covers, or any books whether stacked or standing.
            
            Respond with just the number of books you can count.
            """
            
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64
                }
            ])
            
            # Extract number from response
            count_text = response.text.strip()
            count = int(''.join(filter(str.isdigit, count_text)))
            
            return count
            
        except Exception as e:
            logger.error(f"AI book counting error: {e}")
            return 0

    def batch_process_covers(self, image_paths: List[str]) -> List[Dict]:
        """Process multiple book covers in batch"""
        results = []
        
        for image_path in image_paths:
            result = self.process_book_cover(image_path)
            results.append(result)
            
        return results

    def _error_response(self, message: str) -> Dict:
        """Generate error response"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.datetime.now().isoformat()
        }

# Global instance
image_recognition = AIImageRecognition()

def process_book_cover_image(image_path: str) -> Dict:
    """
    Public function to process book cover image
    
    Args:
        image_path: Path to book cover image
        
    Returns:
        Dict with extracted information
    """
    return image_recognition.process_book_cover(image_path)

def count_books_in_shelf(image_path: str) -> Dict:
    """
    Public function to count books in shelf image
    
    Args:
        image_path: Path to shelf/inventory image
        
    Returns:
        Dict with book count information
    """
    return image_recognition.count_books_in_image(image_path)

def assess_book_damage(image_path: str) -> Dict:
    """
    Public function to assess book damage
    
    Args:
        image_path: Path to book image
        
    Returns:
        Dict with damage assessment
    """
    result = image_recognition.process_book_cover(image_path)
    if result['success']:
        return {
            'success': True,
            'damage_assessment': result['damage_assessment'],
            'timestamp': result['processing_timestamp']
        }
    return result
