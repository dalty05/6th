import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import uuid
from models import db, Product




class QRCodeService:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        
        # Get the absolute path for the static directory
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        self.qr_dir = os.path.join(self.static_dir, 'qr_codes')
        self._ensure_directory()
        
        # Brand colors - Meru Dairy theme
        self.brand_blue = (26, 60, 110)  # #1a3c6e
        self.brand_light_blue = (37, 99, 235)  # #2563eb
        self.brand_white = (255, 255, 255)
        
        # Logo path
        self.logo_path = os.path.join(self.static_dir, 'images', 'meru-dairy-logo.png')
        self.fallback_logo_path = os.path.join(self.static_dir, 'images', 'brand-logo.png')
    
    def _ensure_directory(self):
        """Ensure the QR code directory exists"""
        if not os.path.exists(self.qr_dir):
            os.makedirs(self.qr_dir)
            print(f"✅ Created QR directory: {self.qr_dir}")
    
    def generate_product_qr(self, product_slug, product_name, size=300, include_label=True):
        """
        Generate a branded QR code for a product
        
        Args:
            product_slug: The product's slug
            product_name: The product name
            size: QR code size in pixels
            include_label: Whether to add "Scan to learn more" label
            
        Returns:
            tuple: (qr_code_url, file_path)
        """
        # URL for the product page
        product_url = f"{self.base_url}/product/{product_slug}"
        
        # Generate QR code with rounded modules
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(product_url)
        qr.make(fit=True)
        
        # Create styled QR code with brand colors and rounded modules
        try:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=RadialGradiantColorMask(
                    center_color=(self.brand_blue[0], self.brand_blue[1], self.brand_blue[2], 255),
                    edge_color=(self.brand_light_blue[0], self.brand_light_blue[1], self.brand_light_blue[2], 255)
                )
            )
        except:
            # Fallback to standard QR if styled version fails
            img = qr.make_image(
                fill_color=self.brand_blue,
                back_color=self.brand_white
            )
        
        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Add logo in the center
        img = self._add_logo(img, size)
        
        # Add border with brand colors
        img = self._add_brand_border(img, size)
        
        # Add label text
        if include_label:
            img = self._add_label(img, size)
        
        # Save QR code with brand+product naming
        filename = f"meru-{product_slug}.png"
        filepath = os.path.join(self.qr_dir, filename)
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        img.save(filepath, 'PNG', quality=95)
        print(f"✅ Branded QR code saved: {filepath}")
        
        qr_url = f"/static/qr_codes/{filename}"
        return qr_url, filepath
    
    def _add_logo(self, img, size):
        """Add logo to the center of QR code"""
        logo_paths = [self.logo_path, self.fallback_logo_path]
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path)
                    
                    # Calculate logo size (20% of QR code)
                    logo_size = size // 5
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Create white background circle for logo
                    img = img.convert('RGBA')
                    
                    # Create a white circle background
                    circle_size = logo_size + 20
                    circle = Image.new('RGBA', (circle_size, circle_size), (255, 255, 255, 255))
                    mask = Image.new('L', (circle_size, circle_size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, circle_size, circle_size), fill=255)
                    
                    # Position logo in center
                    x = (size - logo_size) // 2
                    y = (size - logo_size) // 2
                    
                    # Paste logo with mask
                    img.paste(logo, (x, y), logo)
                    
                    return img
                    
                except Exception as e:
                    print(f"Could not add logo from {logo_path}: {e}")
                    continue
        
        return img
    
    def _add_brand_border(self, img, size):
        """Add a brand-themed border around the QR code"""
        # Create new image with border
        border_size = 20
        new_size = size + (border_size * 2)
        
        # Create canvas with brand blue
        bordered = Image.new('RGB', (new_size, new_size), self.brand_blue)
        
        # Add white inner border
        inner_border = 8
        inner_rect = Image.new('RGB', (new_size - (inner_border * 2), new_size - (inner_border * 2)), self.brand_white)
        bordered.paste(inner_rect, (inner_border, inner_border))
        
        # Position QR code in center
        x = (new_size - size) // 2
        y = (new_size - size) // 2
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        bordered.paste(img, (x, y))
        
        return bordered
    
    def _add_label(self, img, size):
        """Add 'Scan to learn more' label below QR code"""
        try:
            # Create new image with extra height for label
            label_height = 40
            new_height = size + label_height
            
            # Create canvas
            labeled = Image.new('RGB', (size, new_height), self.brand_white)
            
            # Paste QR code
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            labeled.paste(img, (0, 0))
            
            # Add label text
            draw = ImageDraw.Draw(labeled)
            
            # Try to load a font, fallback to default
            try:
                # Try to find a system font
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    'C:\\Windows\\Fonts\\arial.ttf',
                    '/System/Library/Fonts/Helvetica.ttc'
                ]
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        font = ImageFont.truetype(path, 14)
                        break
                if not font:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Position text in center
            text = "Scan to learn more"
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (size - text_width) // 2
            text_y = size + 12
            
            draw.text((text_x, text_y), text, fill=self.brand_blue, font=font)
            
            # Add small brand name
            brand_text = "Meru Dairy"
            bbox = draw.textbbox((0, 0), brand_text, font=font)
            brand_width = bbox[2] - bbox[0]
            brand_x = (size - brand_width) // 2
            brand_y = size + 28
            
            draw.text((brand_x, brand_y), brand_text, fill=self.brand_light_blue, font=font)
            
            return labeled
            
        except Exception as e:
            print(f"Could not add label: {e}")
            return img
    
    def regenerate_product_qr(self, product):
        """Regenerate QR code for a product with branding"""
        if not product.slug:
            product.slug = self._generate_unique_slug(product)
        
        # Delete old QR code if exists
        if product.qr_code_url:
            old_filename = product.qr_code_url.split('/')[-1]
            old_path = os.path.join(self.qr_dir, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    print(f"🗑️ Deleted old QR: {old_path}")
                except Exception as e:
                    print(f"Could not delete old QR code: {e}")
        
        # Generate new branded QR code
        qr_url, filepath = self.generate_product_qr(
            product.slug,
            product.name,
            size=300,
            include_label=True
        )
        
        # Also generate a smaller version for thumbnails
        self._generate_thumbnail(product.slug)
        
        product.qr_code_url = qr_url
        product.qr_code_generated_at = datetime.utcnow()
        
        return qr_url
    
    def _generate_thumbnail(self, product_slug):
        """Generate a smaller thumbnail version of the QR code"""
        try:
            # Generate smaller QR code (150px) without label
            self.generate_product_qr(
                product_slug,
                f"{product_slug}-thumb",
                size=150,
                include_label=False
            )
        except Exception as e:
            print(f"Could not generate thumbnail: {e}")
    
    def _generate_unique_slug(self, product):
        """Generate a unique slug for the product"""
        from models import Product
        import re
        
        base_slug = product.name.lower().strip()
        base_slug = re.sub(r'[^a-z0-9\s-]', '', base_slug)
        base_slug = re.sub(r'\s+', '-', base_slug)
        base_slug = re.sub(r'-+', '-', base_slug)
        
        slug = base_slug
        counter = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def delete_product_qr(self, product):
        """Delete QR code file for a product"""
        if product.qr_code_url:
            old_filename = product.qr_code_url.split('/')[-1]
            old_path = os.path.join(self.qr_dir, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    print(f"🗑️ Deleted QR: {old_path}")
                except Exception as e:
                    print(f"Could not delete QR code: {e}")
            product.qr_code_url = None
            product.qr_code_generated_at = None
    

    def batch_regenerate_all(self):
        """Regenerate QR codes for all products"""
        from models import Product, db  # ✅ Import db here too
        
        products = Product.query.all()
        count = 0
        
        for product in products:
            try:
                self.regenerate_product_qr(product)
                db.session.add(product)
                count += 1
                print(f"✅ Generated QR for: {product.name}")
            except Exception as e:
                print(f"❌ Failed for {product.name}: {e}")
        
        db.session.commit()
        print(f"\n✅ Batch complete! Generated {count} QR codes")
        return count