
import pytest
from pydantic import ValidationError
from src.core.models import TextRequest, ImageProcessRequest

class TestValidation:
    """Input validation tests"""

    def test_text_request_valid(self):
        """Test valid TextRequest"""
        req = TextRequest(text="Hello world", seasoning=50)
        assert req.text == "Hello world"
        assert req.seasoning == 50

    def test_text_request_too_long(self):
        """Test TextRequest with text exceeding max length"""
        long_text = "a" * 20001
        with pytest.raises(ValidationError) as excinfo:
            TextRequest(text=long_text, seasoning=30)

        errors = excinfo.value.errors()
        assert any(e['type'] == 'string_too_long' for e in errors)

    def test_text_request_seasoning_min(self):
        """Test TextRequest with seasoning below 0"""
        with pytest.raises(ValidationError) as excinfo:
            TextRequest(text="test", seasoning=-1)

        errors = excinfo.value.errors()
        assert any(e['type'] == 'greater_than_equal' for e in errors)

    def test_text_request_seasoning_max(self):
        """Test TextRequest with seasoning above 100"""
        with pytest.raises(ValidationError) as excinfo:
            TextRequest(text="test", seasoning=101)

        errors = excinfo.value.errors()
        assert any(e['type'] == 'less_than_equal' for e in errors)

    def test_image_request_seasoning_validation(self):
        """Test ImageProcessRequest seasoning validation"""
        with pytest.raises(ValidationError):
            ImageProcessRequest(image_base64="dGVzdA==", seasoning=150)

        # Valid case
        req = ImageProcessRequest(image_base64="dGVzdA==", seasoning=0)
        assert req.seasoning == 0
