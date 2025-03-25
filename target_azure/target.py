"""Azure Storage target class."""

from __future__ import annotations
from singer_sdk import typing as th
from singer_sdk.target_base import Target
from target_azure.sinks import TargetAzureBlobSink

class TargetAzureStorage(Target):
    """Sample target for Azure Storage."""

    name = "target-azure"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "internal_log_level",
            th.StringType,
            required=False,
            description="DEBUG, INFO, etc.",
        ),
        th.Property(
            "subfolder_path",
            th.StringType,
            required=False,
            description="""
                The format of the sub folder to use. Use {stream}, {date}, {time} and {timestamp} as variables.
                For onelake, this must start with Files or Tables.
            """,
        ),

        th.Property(
            "local_temp_folder",
            th.StringType,
            required=False,
            description="Temp folder to use to stage csv files before uploading.  Defaults to the os default temp folder",
        ),
        th.Property(
            "write_header",
            th.StringType,
            required=False,
            description="Should headers be written for every CSV file.  Defaults to False.",
        ),
        th.Property(
            "csv_encoding",
            th.StringType,
            required=False,
            description="The text encoding of the CSV file.  Defaults to UTF-8",
        ),
        th.Property(
            "create_container_if_missing",
            th.StringType,
            required=False,
            description="""
            Should an attempt be made to create the Azure Blob container?  Defaults to False.
            For Fabric OneLake this should be set to false.
            """,
        ),
        th.Property(
            "naming_convention",
            th.StringType,
            description="""
                The format of the file location. Use {stream}, {date}, {time} and {timestamp} as variables.
                You can also define different file formats: 'parquet', 'json', 'jsonlines' and 'csv'.
            """,
        ),


        th.Property(
            "auth_method",
            th.StringType,
            required=True,
            description="""
            The Authentication method to use, Service Principal (servicePrincipal) or Storage Account Key (accountKey)
            Service Principal must be used for Fabric Onelake.
            """,
        ),
        th.Property(
            "storage_account_name",
            th.StringType,
            required=True,
            description="Azure storage account name.  For Fabric OneLake use 'onelake'",
        ),
        th.Property(
            "storage_account_key",
            th.StringType,
            description="""
            Azure storage account key.
            Only required when using the 'accountKey' auth method.
            """,
        ),
        th.Property(
            "container_name",
            th.StringType,
            required=True,
            description="""
            The Azure Blob Storage container name where the files will be stored.
            For Onelake, this is the Workspace and Lakehouse name in the <Workspace>/<lakehouseName>.Lakehouse
            """
        ),

        th.Property(
            "tenant_id",
            th.StringType,
            required=False,
            description="The Azure Tenant Id.  Required for servicePrincipal authentication",
        ),
        th.Property(
            "app_id",
            th.StringType,
            required=False,
            description="The Entra Service Principal Application Id.  Required for servicePrincipal authentication",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=False,
            description="The Entra Service Principal Client Secret.  Required for servicePrincipal authentication",
        ),
        th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="""
                The Base URL for the Azure Blob storage service.
                For Azure Blob Storage / ADLS Gen 2: core.windows.net
                For Fabric Onelake: fabric.microsoft.com
                See Azure documentation for other storage urls.
            """,
        )
    ).to_dict()

    default_sink_class = TargetAzureBlobSink

if __name__ == "__main__":
    TargetAzureStorage.cli()

