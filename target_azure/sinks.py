import os
import pandas as pd
from singer_sdk.sinks import BatchSink
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential
import re
import logging
from azure.core.exceptions import ResourceExistsError
from datetime import datetime
import atexit
import tempfile

class TargetAzureBlobSink(BatchSink):
    """Azure Storage target sink class for streaming."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_initialized = False
        logLevel = self.config.get("internal_log_level", logging.INFO)
        self.logger.setLevel(logLevel)
        atexit.register(self.finalize)

    def start_stream(self) -> None:
        """Initialize the stream."""
        self.logger.info(f"Starting stream for {self.stream_name}")

        self.container_client = None

        self.blob_subfolder = self.config.get("subfolder_path", "default_subfolder_path")
        self.local_temp_folder = self.config.get("local_temp_folder", tempfile.gettempdir())
        
        self.write_header = self.config.get("write_header", False)
        self.csv_encoding = self.config.get("csv_encoding", 'UTF-8')
        self.create_container_if_missing = self.config.get("create_container_if_missing", False)
        self.naming_convention = self.config.get("naming_convention", "{stream}.csv")


        container_name = None
        BASE_URL = self.config.get("base_url", "core.windows.net")

        if self.config["auth_method"] == "accountKey":
            account_name = self.config["storage_account_name"]
            account_key = self.config["storage_account_key"]
            container_name = self.config.get("container_name", "default-container")
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix={BASE_URL}"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_client = blob_service_client.get_container_client(container_name)

        if self.config["auth_method"] == "servicePrincipal":
            TENANT_ID = self.config["tenant_id"]
            CLIENT = self.config["app_id"]
            KEY = self.config["client_secret"]
            ACCOUNT_NAME = self.config["storage_account_name"]
            container_name = self.config.get("container_name", "default-container")
            

            credentials = ClientSecretCredential(TENANT_ID, CLIENT, KEY)

            blobstring = f"https://{ACCOUNT_NAME}.blob.{BASE_URL}"

            self.logger.debug(f"Blob URL: {blobstring}")

            blobService = BlobServiceClient(
                blobstring,
                credential=credentials
                )
            self.container_client = blobService.get_container_client(container_name)

        if not self.container_client:
            self.logger.error("No Conatiner client to was created  There is a config issue.")
            return
        
        if self.create_container_if_missing:
            try:
                self.container_client.create_container()
                self.logger.info(f"Created container: {container_name}")
            except ResourceExistsError:
                self.logger.info(f"Container {container_name} already exists.")
        
        os.makedirs(self.local_temp_folder, exist_ok=True)
        self.stream_initialized = True

    def process_batch(self, context: dict):
        if not self.stream_initialized:
            self.start_stream()

        if not self.local_temp_folder:
            self.logger.error("local_temp_folder is None.")
            return
        
        if not self.container_client:
            self.logger.error("No Conatiner client to upload files with.")
            return
        
        local_file_name = self.format_file_name()
        local_file_path = os.path.join(self.local_temp_folder, local_file_name)
        blob_subfolder = self.format_blob_subfolder()

        try:

            df = pd.DataFrame(context["records"])
            df.to_csv(local_file_path, mode='w', index=False, header=self.write_header, encoding=self.csv_encoding, errors='replace')
        except Exception as e:
            self.logger.error(f"Failed to write file.  Dataframe {df}")

            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                self.logger.debug(f"Removed local file: {local_file_path}")
            else:
                self.logger.error(f"Local file not found during cleanup: {local_file_path}")
            raise

        self.logger.debug(f"wrote {df.__len__()} lines to {local_file_path}")

        self.logger.debug(f"Preparing to upload {local_file_path} to Azure Blob Storage")

        try:
            # Check if file exists before uploading
            if not os.path.exists(local_file_path):
                self.logger.error(f"Local file does not exist: {local_file_path}")
                return

            with open(local_file_path, "rb") as data:
                blob_path = os.path.join(blob_subfolder, local_file_name)

                blob_client = self.container_client.get_blob_client(blob=blob_path)

                blob_client.upload_blob(data, overwrite=True)
            self.logger.info(f"Successfully uploaded {blob_path} to Azure Blob Storage")
        except Exception as e:
            self.logger.error(f"Failed to upload {blob_path} to Azure Blob Storage: {e}")
            raise
        finally:
            # Clean up the local file after upload
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                self.logger.debug(f"Removed local file: {local_file_path}")
            else:
                self.logger.error(f"Local file not found during cleanup: {local_file_path}")

    def format_file_name(self) -> str:
        """Format the file name based on the context and Azure Blob Storage naming rules."""
        naming_convention = self.naming_convention  # Provide a default naming convention
        stream_name = self.stream_name
        file_name = naming_convention.replace("{stream}", stream_name).replace("{date}", str(datetime.now().date())).replace("{time}", str(datetime.now().time())).replace("{timestamp}", str(datetime.now().timestamp()))



        file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)  # Replace or remove invalid characters for Azure Blob Storage

        self.logger.debug(f"Formatted file name: {file_name}")
        return file_name
    
    def format_blob_subfolder(self) -> str:
        """Format the file name based on the context and Azure Blob Storage naming rules."""
        naming_convention = self.blob_subfolder  # Provide a default naming convention
        stream_name = self.stream_name
        file_name = naming_convention.replace("{stream}", stream_name).replace("{date}", str(datetime.now().date())).replace("{time}", str(datetime.now().time())).replace("{timestamp}", str(datetime.now().timestamp()))



        #file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)  # Replace or remove invalid characters for Azure Blob Storage

        self.logger.debug(f"Formatted blob folder name: {file_name}")
        return file_name

    def finalize(self) -> None:
        self.logger.info(f"Finalizing stream for {self.stream_name}")
        self.logger.info(f"Successfully finalized stream for {self.stream_name}")

if __name__ == "__main__":
    TargetAzureBlobSink.cli()