import json
import boto3
import xml.etree.ElementTree as et
import bs4
import uuid
import io
import zipfile
import pyarrow as pa
from pyarrow import parquet as pq
import pyarrow.json as pa_json
import pyarrow.compute as pc

sts = boto3.client("sts")
s3 = boto3.client("s3")
biorxiv_bucket = "biorxiv-src-monthly"
agbiome_bucket = "<bucket_name_goes_here"

role_assumption = "arn:aws:iam::<insert-account-here>:role/cross-account-ec2"

response = sts.assume_role(
    RoleArn=role_assumption, RoleSessionName="test-session", DurationSeconds=43000
)

print(response)

access_key = response["Credentials"]["AccessKeyId"]
secret_key = response["Credentials"]["SecretAccessKey"]
session_token = response["Credentials"]["SessionToken"]

assumed_role_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    aws_session_token=session_token,
    region_name="us-west-2",
)

print("assumed_role_client...")
print("Reading file list...")

file_list = (
    assumed_role_client.get_object(Key="{}", Bucket="agbiome-temp-biorxiv")["Body"]
    .read()
    .decode()
    .split("\\n")
)


def clean_xml2(content, filename):
    try:
        print("attempting to clean xml...")
        file_info = {}
        root = et.fromstring(content)
        xml_data = et.tostring(root)
        soup = bs4.BeautifulSoup(xml_data)

        accepted = soup.find("date", {"date-type": "accepted"})
        day = accepted.find("day").text
        month = accepted.find("month").text
        year = accepted.find("year").text
        date = "-".join([year, month, day])

        file_info["title"] = soup.find("title-group").find("article-title").text
        file_info["abstract"] = soup.find("abstract").p.text
        file_info["text_body"] = ";".join([para.text for para in soup.find_all("p")])
        file_info["article_id"] = soup.find("article-id").text
        file_info["date_accepted"] = date
        file_info["text_body_object_id"] = str(uuid.uuid4()) + ".txt"
        file_info["biorxiv_keyname"] = filename
        file_info["parquet_file_id"] = filename.split("/")[-1].replace(
            ".meca", ".parquet"
        )
        file_info["category"] = (
            soup.find("subj-group", {"subj-group-type": "hwp-journal-coll"})
            .find("subject")
            .text.lower()
        )

    except Exception as e:
        print(e.args)

    return file_info


def bytes_to_megabytes(size_in_bytes):
    return round(size_in_bytes / (1024 * 1024), 2)


def extract_data(file_name):
    try:
        print(f"Retrieving file {file_name}")
        response = assumed_role_client.get_object(
            Bucket=biorxiv_bucket, Key=file_name, RequestPayer="requester"
        )
        print(response["ResponseMetadata"]["HTTPStatusCode"])
        print("Unzipping...")
        with zipfile.ZipFile(io.BytesIO(response["Body"].read()), "r") as zipf:
            file_names = zipf.namelist()
            xml_files = [
                name
                for name in file_names
                if name.startswith("content") and name.endswith(".xml")
            ]
            for xml_file in xml_files:
                extracted_file_data = zipf.read(xml_file).decode()
        cleaned = clean_xml2(extracted_file_data, file_name)
    except Exception as e:
        print(e.args)

    return cleaned


def write_text_body(obj):
    try:
        print("Writing text body...")
        data = bytes(obj["text_body"].encode("utf-8"))
        resp = assumed_role_client.put_object(
            Bucket=agbiome_bucket,
            Key="text_bodies/{}.txt".format(obj["text_body_object_id"]),
            Body=data,
        )
    except Exception as e:
        print(e.args)
    return resp


def write_parquet(obj):
    try:
        print("Formatting data for parquet...")
        filtered_dict = {
            key: value for key, value in obj.items() if not key == "text_body"
        }
        schema = pa.schema(
            [
                ("title", pa.string()),
                ("abstract", pa.string()),
                ("article_id", pa.string()),
                ("date_accepted", pa.string()),
                ("text_body_object_id", pa.string()),
                ("biorxiv_keyname", pa.string()),
                ("parquet_file_id", pa.string()),
                ("category", pa.string()),
            ]
        )
        json_str = json.dumps(filtered_dict)
        json_file_like = io.BytesIO(json_str.encode())
        parse_options = pa_json.ParseOptions(explicit_schema=schema)
        table = pa_json.read_json(json_file_like, parse_options=parse_options)
        final_table = table.set_column(
            table.schema.get_field_index("date_accepted"),
            "date_accepted",
            pc.strptime(table["date_accepted"], format="%Y-%m-%d", unit="s").cast(
                pa.date32()
            ),
        )
        b = io.BytesIO()
        pq.write_table(final_table, b)
        b.seek(0)

        print("Uploading to s3...")
        # This is calling s3 via the role of the client
        resp = assumed_role_client.put_object(
            Bucket=agbiome_bucket,
            Key="parquet/category={}/{}".format(
                filtered_dict["category"], filtered_dict["parquet_file_id"]
            ),
            Body=b.read(),
        )
    except Exception as e:
        print(e.args)
    return final_table


def write(filename):
    obj = extract_data(filename)
    table = write_parquet(obj)
    text = write_text_body(obj)

    return (text, table)


for filename in file_list:
    try:
        write(filename)
    except Exception as e:
        print(e.args)
        try:
            assumed_role_client.put_object(
                Bucket=agbiome_bucket,
                Key="failed_files/{}".format(filename),
                Body=bytes(str(filename).encode()),
            )
        except Exception as e:
            print(e.args)
