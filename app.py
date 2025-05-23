import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from services.product_service import ProductService
from services.firebase_service import FirebaseService
from utils.image_utils import process_image, download_image
import tempfile
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

product_service = ProductService({
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
})
firebase_service = FirebaseService()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/search-by-image', methods=['POST'])
def search_by_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Process the uploaded image
            query_features = process_image(temp_path)
            
            # Get all products with image URLs
            products = product_service.get_all_products()
            
            # Compare with each product image
            results = []
            for product in products:
                if product['image_url']:
                    try:
                        # Download product image from Firebase
                        image_url = product['image_url'].split(',')[0]
                        product_image_path = download_image(image_url)
                        product_features = process_image(product_image_path)
                        
                        # Calculate similarity
                        similarity = product_service.calculate_similarity(
                            query_features, 
                            product_features
                        )
                        
                        if similarity >= 0.4:
                            results.append({
                                'id': product['id'],
                                'productCode': product['product_code'],
                                'name': product['name'],
                                'price': product['price'],
                                'description': product['description'],
                                'totalQuantity': product['total_quantity'],
                                'soldQuantity': product['sold_quantity'],
                                'rating': product['rating'],
                                'discount': product['discount'],
                                'imageUrl': product['image_url'].split(','),
                                'isActive': product['is_active'],
                                'category': json.loads(product['category']),
                                'variants': json.loads(product['variants']),
                                'similarity': float(similarity)
                            })
                        
                        # Clean up downloaded image
                        if os.path.exists(product_image_path):
                            os.remove(product_image_path)
                    except Exception as e:
                        print(f"Error processing product {product['id']}: {str(e)}")
                        continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return jsonify({
                'data': {
                    'items': results
                },
                'pagination': {
                    'totalItems': results.__len__(),
                    'totalPages': 0
                },
                'code': 200,
                'message': 'Thành công',
                'success': True
            })
            
        finally:
            # Clean up uploaded file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/')
def index():
    return product_service.get_all_products()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)