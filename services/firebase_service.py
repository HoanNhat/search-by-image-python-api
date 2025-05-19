import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseService:
    def __init__(self):
        # Initialize Firebase
        cred = credentials.Certificate({
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        })
        
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def get_product_image_urls(self):
        """Get all product image URLs from Firebase"""
        products_ref = self.db.collection('products')
        docs = products_ref.stream()
        
        return [
            {'id': doc.id, 'image_url': doc.to_dict().get('image_url')} 
            for doc in docs 
            if doc.to_dict().get('image_url')
        ]