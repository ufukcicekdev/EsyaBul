from storages.backends.s3boto3 import S3Boto3Storage
import os
import uuid

class CustomS3Boto3Storage(S3Boto3Storage):
    def get_available_name(self, name, max_length=None):
        base_name, ext = os.path.splitext(name)
        random_hex = uuid.uuid4().hex
        new_name = f"{base_name}_{random_hex}{ext}"
        folder_name = self.location
        final_name = os.path.join(folder_name, new_name)
        return super().get_available_name(final_name, max_length)
