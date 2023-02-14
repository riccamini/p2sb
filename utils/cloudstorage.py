from dotenv import load_dotenv
load_dotenv()

from google.cloud import storage
import logging
import shutil
import os

logging.basicConfig(
    level=os.getenv('LOG_LEVEL'),
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)

class CloudStorageClient:

    def __init__(self):

        if os.getenv('CS_IMPL') is not None and os.getenv('CS_IMPL') == 'LOCAL_STORAGE':
            self.is_mock = True
            self.cs_client = None
            self.mock_bucket_dir = os.getenv('MOCK_BUCKET_DIR')

            # Check if mock bucket dir exists otherwise creates it
            if not os.path.isdir(self.mock_bucket_dir) and self.mock_bucket_dir is not None:
                os.mkdir(self.mock_bucket_dir)

        else:
            self.cs_client = storage.Client()
            self.is_mock = False

    def _get_object_mock(self, bucket_name, object_name, file_path):
        logger.debug(f"Downloading {object_name} from bucket {object_name} into {file_path}")
        shutil.copy2(self.mock_bucket_dir+f"/{object_name}", file_path)
    
    def _get_object(self, bucket_name, object_name, file_path):
        logger.debug(f"Downloading {object_name} from bucket {object_name} into {file_path}")

        bucket = self.cs_client.bucket(bucket_name)
        blob = bucket.blob(object_name)

        blob.download_to_filename(file_path)

    def get_object(self, bucket_name: str, object_name: str, file_path: str):
        if self.is_mock:
            self._get_object_mock(bucket_name, object_name, file_path)
        else:
            self._get_object(bucket_name, object_name, file_path)

    def _put_object_mock(self, bucket_name, object_name, file_path):
        destination_path = self.mock_bucket_dir+f"/{object_name}"
        logger.debug(f"Uploading {file_path} to {destination_path}")

        shutil.copy2(file_path,  destination_path)
    
    def _put_object(self, bucket_name, object_name, file_path):
        logger.debug(f"Uploading {file_path} to {bucket_name}/{object_name}")

        bucket = self.cs_client.bucket(bucket_name)
        blob = bucket.blob(object_name)

        blob.upload_from_filename(file_path)
    
    def put_object(self, bucket_name: str, object_name: str, file_path: str):
        if self.is_mock:
            self._put_object_mock(bucket_name, object_name, file_path)
        else:
            self._put_object(bucket_name, object_name, file_path)
