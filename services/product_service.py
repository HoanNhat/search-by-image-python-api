from utils.model_utils import cosine_similarity
import numpy as np
import pymysql
from pymysql import Error
from pymysql.cursors import DictCursor
from typing import List, Dict, Optional

class ProductService:
    def __init__(self, db_config: Dict):
        """Khởi tạo kết nối database
        
        Args:
            db_config (Dict): Cấu hình kết nối MySQL gồm:
                - host
                - database
                - user
                - password
                - port
        """
        self.db_config = db_config
        self.connection = None
        
    def __enter__(self):
        """Kết nối database khi sử dụng with statement"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Đóng kết nối khi thoát with statement"""
        self.disconnect()
        
    def connect(self):
        """Thiết lập kết nối MySQL"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port'],
                charset='utf8mb4',
                cursorclass=DictCursor
            )
        except Error as e:
            print(f"Lỗi khi kết nối MySQL: {e}")
            raise
            
    def disconnect(self):
        """Đóng kết nối MySQL"""
        if self.connection and self.connection.open:
            self.connection.close()
            
    def get_all_products(self) -> List[Dict]:
        """Lấy tất cả sản phẩm có URL hình ảnh từ database
        
        Returns:
            List[Dict]: Danh sách sản phẩm
        """
        cursor = None  # Khởi tạo trước để tránh UnboundLocalError
        if not self.connection or not self.connection.open:
            self.connect()
            
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT 
                    p.id,
                    p.product_code ,
                    p.name,
                    p.price,
                    p.description,
                    p.total_quantity,
                    p.sold_quantity,
                    p.rating,
                    p.discount,
                    p.image_url,
                    p.created_at,
                    p.updated_at,
                    p.is_active,
                    JSON_OBJECT(
                        'id', c.id,
                        'name', c.name
                    ) AS category,
                    JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'id', pv.id,
                            'size', pv.size,
                            'color', pv.color,
                            'colorHex', pv.color_hex,
                            'quantity', pv.quantity
                        )
                    ) AS variants
                FROM 
                    products p
                LEFT JOIN 
                    categories c ON p.category_id = c.id
                LEFT JOIN 
                    product_variants pv ON p.id = pv.product_id
                WHERE 
                    p.is_active = TRUE
                AND
                    p.image_url IS NOT NULL
                GROUP BY 
                    p.id, p.product_code, p.name, p.price, p.description, 
                    p.total_quantity, p.sold_quantity, p.rating, p.discount, 
                    p.image_url, p.created_at, p.updated_at, p.is_active, 
                    c.id, c.name
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy sản phẩm: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Lấy thông tin chi tiết sản phẩm theo ID
        
        Args:
            product_id (int): ID sản phẩm
            
        Returns:
            Optional[Dict]: Thông tin sản phẩm hoặc None nếu không tìm thấy
        """
        cursor = None  # Khởi tạo trước để tránh UnboundLocalError
        if not self.connection or not self.connection.open:
            self.connect()
            
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT id, name, description, image_url 
                FROM products 
                WHERE id = %s
            """
            cursor.execute(query, (product_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Lỗi khi lấy sản phẩm theo ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def calculate_similarity(self, vec1, vec2) -> float:
        """Tính độ tương đồng cosine giữa hai vector đặc trưng
        
        Args:
            vec1: Vector đặc trưng thứ nhất
            vec2: Vector đặc trưng thứ hai
            
        Returns:
            float: Độ tương đồng cosine (0-1)
        """
        return cosine_similarity(vec1, vec2)