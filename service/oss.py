import oss2


class OSSClient:
    def __init__(self, access_key_id, access_key_secret, endpoint, bucket_name):
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)

    def upload_file(self, local_file, oss_path):
        try:
            self.bucket.put_object_from_file(oss_path, local_file)
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def download_file(self, oss_path, local_file):
        try:
            self.bucket.get_object_to_file(oss_path, local_file)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    def delete_file(self, oss_path):
        try:
            self.bucket.delete_object(oss_path)
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
