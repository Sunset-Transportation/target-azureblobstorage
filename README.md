# target-azure

`target-azure` is a Singer target for tap-azure.

Build with the [Meltano Target SDK](https://sdk.meltano.com).

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPi:

```bash
pipx install target-azure
```

Install from GitHub:

```bash
pipx install git+https://github.com/ORG_NAME/target-azure.git@main
```

-->

## Configuration

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| internal_log_level | False    | INFO    | DEBUG, INFO, etc. |
| subfolder_path | False    | Files   | <BR/>                The format of the sub folder to use. Use {stream}, {date}, {time} and {timestamp} as variables.<BR/>                For onelake, this must start with Files or Tables.<BR/>             |
| local_temp_folder | False    | \%temp\% on windows or /tmp on linux | Temp folder to use to stage csv files before uploading.  Defaults to the os default temp folder |
| write_header | False    | False   | Should headers be written for every CSV file. |
| csv_encoding | False    | UTF-8   | The text encoding of the CSV file. |
| create_container_if_missing | False    | False   | <BR/>            Should an attempt be made to create the Azure Blob container?  Defaults to False.<BR/>            For Fabric OneLake this should be set to false.<BR/>             |
| naming_convention | False    | {stream}.csv | <BR/>                The format of the file location. Use {stream}, {date}, {time} and {timestamp} as variables.<BR/>                You can also define different file formats: 'parquet', 'json', 'jsonlines' and 'csv'.<BR/>             |
| auth_method | True     | None    | <BR/>            The Authentication method to use, Service Principal (servicePrincipal) or Storage Account Key (accountKey)<BR/>            Service Principal must be used for Fabric Onelake.<BR/>             |
| storage_account_name | True     | None    | Azure storage account name.  For Fabric OneLake use 'onelake' |
| storage_account_key | False    | None    | <BR/>            Azure storage account key.<BR/>            Only required when using the 'accountKey' auth method.<BR/>             |
| container_name | True     | None    | <BR/>            The Azure Blob Storage container name where the files will be stored.<BR/>            For Onelake, this is the Workspace and Lakehouse name in the <Workspace>/<lakehouseName>.Lakehouse<BR/>             |
| tenant_id | False    | None    | The Azure Tenant Id.  Required for servicePrincipal authentication |
| app_id | False    | None    | The Entra Service Principal Application Id.  Required for servicePrincipal authentication |
| client_secret | False    | None    | The Entra Service Principal Client Secret.  Required for servicePrincipal authentication |
| base_url | True     | core.windows.net | <BR/>                The Base URL for the Azure Blob storage service.<BR/>                For Azure Blob Storage / ADLS Gen 2: core.windows.net<BR/>                For Fabric Onelake: fabric.microsoft.com<BR/>                See Azure documentation for other storage urls.<BR/>             |
| add_record_metadata | False    | None    | Add metadata to records. |
| load_method | False    | TargetLoadMethods.APPEND_ONLY | The method to use when loading data into the destination. `append-only` will always write all input records whether that records already exists or not. `upsert` will update existing records and insert new records. `overwrite` will delete all existing records and insert all input records. |
| batch_size_rows | False    | None    | Maximum number of rows in each batch. |
| validate_records | False    |       1 | Whether to validate the schema of the incoming streams. |
| stream_maps | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config | False    | None    | User-defined config values to be used within map expressions. |
| faker_config | False    | None    | Config for the [`Faker`](https://faker.readthedocs.io/en/master/) instance variable `fake` used within map expressions. Only applicable if the plugin specifies `faker` as an addtional dependency (through the `singer-sdk` `faker` extra or directly). |
| faker_config.seed | False    | None    | Value to seed the Faker generator for deterministic output: https://faker.readthedocs.io/en/master/#seeding-the-generator |
| faker_config.locale | False    | None    | One or more LCID locale strings to produce localized output for: https://faker.readthedocs.io/en/master/#localization |
| flattening_enabled | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth | False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `target-azure --about`

## Configuring for Azure Blob Storage

## Configuring for Fabric Lakehouse

When uploading to Microsoft Fabric Lakehouse via the [Azure BlobServiceClient](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-dotnet-get-started?tabs=azure-ad) there are some special configuration settings that must be used.

* Authentication *MUST* be Service Principal.  
* The storage account name for all of onelake is `onelake`
* the container name is the name of the Workspace and Lakehouse (`{WorkSpaceName}/{Lakehouse Name}`).
* The subfolder path *MUST* be `Files` or `Tables`
* The base_url should be set to `fabric.microsoft.com`
* Attempt Container Creation must be set to False because that is not allowed for the OneLake endpoints.

## Authentication methods

### Service Principal

The service principal must be assigned the `Storage Blob Data Contributor` and `Storage Queue Data Contributor` roles on the Azure Blob storage account

### Configure using environment variables

This Singer target will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `target-azure` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Target Directly

```bash
target-azure --version
target-azure --help
# Test using the "Carbon Intensity" sample:
tap-carbon-intensity | target-azure --config /path/to/target-azure-config.json
```


## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `target-azure` CLI interface directly using `poetry run`:

```bash
poetry run target-azure --help
```

### Testing with [Meltano](https://meltano.com/)

_**Note:** This target will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd target-azure
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke target-azure --version
# OR run a test `elt` pipeline with the Carbon Intensity sample tap:
meltano run tap-carbon-intensity target-azure
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the Meltano Singer SDK to
develop your own Singer taps and targets.
