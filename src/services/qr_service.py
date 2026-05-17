import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
from pathlib import Path
import os

class QRService:
    @staticmethod
    def generate_qr(data):
        """Generates a QR code image from the provided data."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img

    @staticmethod
    def save_qr_to_desktop(img, filename):
        """Saves the QR image to the user's Desktop."""
        try:
            desktop_path = Path.home() / "Desktop"
            full_path = desktop_path / filename
            img.save(full_path)
            return True, str(full_path)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def decode_qr_image(file_path):
        """Decodes a QR code image and returns the data."""
        try:
            img = Image.open(file_path)
            decoded_objects = decode(img)
            if decoded_objects:
                return True, decoded_objects[0].data.decode('utf-8')
            return False, "No QR code found in image."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def parse_qr_data(qr_text):
        """Parses the specialized QR data format into a dictionary."""
        # Format: BANK=...;ACCOUNT=...;PHONE=...;USER=...;
        data = {}
        parts = qr_text.split(';')
        for part in parts:
            if '=' in part:
                key, val = part.split('=', 1)
                data[key.strip()] = val.strip()
        return data
