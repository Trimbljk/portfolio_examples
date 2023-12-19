import boto3
import logging
import os
import json
import uuid

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
glue = boto3.client("glue")
lf = boto3.client("lakeformation")
s3 = boto3.client("s3")

bucket = os.environ["BUCKETNAME"]
LOGGER.info(f"BUCKET: {bucket}")
output_path = os.environ["PERMISSIONS_PATH"]
LOGGER.info(f"PATH: {output_path}")


def get_databases(event, context):
    """Get all databases from Glue"""

    LOGGER.info("Gathering databases...")
    dbs = glue.get_databases()["DatabaseList"]

    dblist = []
    for db in dbs:
        LOGGER.info(f"Checking {db}")
        if "TargetDatabase" in db.keys():
            dblist.append(
                {
                    "name": db["Name"],
                    "catalogId": db["CatalogId"],
                    "link": "true",
                    "linkId": db["TargetDatabase"]["CatalogId"],
                    "linkName": db["TargetDatabase"]["DatabaseName"],
                }
            )
            LOGGER.info(f"Adding db: {db}")
        else:
            dblist.append(
                {
                    "name": db["Name"],
                    "catalogId": db["CatalogId"],
                    "link": "false",
                    "linkId": "NA",
                    "linkName": "NA",
                }
            )
            LOGGER.info(f"Adding db in else: {db}")
    LOGGER.info(dblist)

    return {"databases": dblist}


def get_tables(event, context):
    """Get all tables from all databases from Glue
    and grab the catalog ID. Tables that are generated
    from a link will list the account catalog id and a
    return the source catalog id in another key"""

    LOGGER.info(event)
    LOGGER.info("Gathering tables...")
    if event["link"] == "true":
        resp = glue.get_tables(DatabaseName=event["name"], CatalogId=event["linkId"])[
            "TableList"
        ]
        event["linkTables"] = [{"name": t["Name"], "id": t["CatalogId"]} for t in resp]

    resp = glue.get_tables(DatabaseName=event["name"])["TableList"]

    event["Tables"] = [{"name": t["Name"], "id": t["CatalogId"]} for t in resp]

    return event


def get_permissions(event, context):
    #    allperms = {
    #        "Arn": [],
    #        "role_name": [],
    #        "Resource": [],
    #        "catalog_id": [],
    #        "Table_name": [],
    #        "Database_name": [],
    #        "Permissions": [],
    #        "Grants": [],
    #        "column_wild": [],
    #    }
    allFiles = []
    for db in event:
        allperms = {
            "Arn": [],
            "role_name": [],
            "Resource": [],
            "catalog_id": [],
            "Table_name": [],
            "Database_name": [],
            "Permissions": [],
            "Grants": [],
            "column_wild": [],
        }
        dbs_and_links = []
        db_perms = lf.list_permissions(
            Resource={"Database": {"Name": db["name"], "CatalogId": db["catalogId"]}}
        )["PrincipalResourcePermissions"]

        dbs_and_links.append(db_perms)
        if db["linkName"] == "NA":
            pass
        else:
            db_perms = lf.list_permissions(
                Resource={
                    "Database": {"Name": db["linkName"], "CatalogId": db["linkId"]}
                }
            )["PrincipalResourcePermissions"]
            dbs_and_links.append(db_perms)

        for dl in dbs_and_links:
            for p in dl:
                """Unless otherwise specified, grab all the columns
                For everytable"""
                allperms["Arn"].append(p["Principal"]["DataLakePrincipalIdentifier"])
                allperms["Resource"].append("Database")
                allperms["Table_name"].append(p["Resource"]["Database"]["Name"])
                allperms["Database_name"].append(db["name"])
                allperms["Permissions"].append(p["Permissions"])
                allperms["Grants"].append(p["PermissionsWithGrantOption"])
                allperms["column_wild"].append("-")
                allperms["catalog_id"].append(p["Resource"]["Database"]["CatalogId"])

                """IAM_ALLOW_PRINCIPALS is the backwards compatibility of
                    Lake Formation with IAM"""

                if (
                    p["Principal"]["DataLakePrincipalIdentifier"]
                    == "IAM_ALLOWED_PRINCIPALS"
                ):
                    allperms["role_name"].append(
                        p["Principal"]["DataLakePrincipalIdentifier"]
                    )
                else:
                    allperms["role_name"].append(
                        p["Principal"]["DataLakePrincipalIdentifier"].split("/")[1]
                    )

        for table in db["Tables"]:
            """A role that has a permission on all tables won't
            show up when querying a single table. You have to pass
            the 'TableWildcard' parameter in a seperate call"""

            singletable = lf.list_permissions(
                Resource={
                    "Table": {
                        "DatabaseName": db["name"],
                        "Name": table["name"],
                        "CatalogId": str(table["id"]),
                    }
                }
            )["PrincipalResourcePermissions"]

            alltables = lf.list_permissions(
                Resource={"Table": {"DatabaseName": db["name"], "TableWildcard": {}}}
            )["PrincipalResourcePermissions"]

            rl = [alltables, singletable]

            for tab in rl:
                for tp in tab:
                    allperms["Arn"].append(
                        tp["Principal"]["DataLakePrincipalIdentifier"]
                    )
                    allperms["Permissions"].append(tp["Permissions"])
                    allperms["Database_name"].append(db["name"])
                    allperms["Grants"].append(tp["PermissionsWithGrantOption"])
                    if (
                        tp["Principal"]["DataLakePrincipalIdentifier"]
                        == "IAM_ALLOWED_PRINCIPALS"
                    ):
                        allperms["role_name"].append(
                            tp["Principal"]["DataLakePrincipalIdentifier"]
                        )
                    else:
                        allperms["role_name"].append(
                            tp["Principal"]["DataLakePrincipalIdentifier"].split("/")[
                                -1
                            ]
                        )

                    if "Table" in tp["Resource"].keys():
                        allperms["Resource"].append("Table")
                        allperms["Table_name"].append(tp["Resource"]["Table"]["Name"])
                        allperms["column_wild"].append("-")
                        allperms["catalog_id"].append(
                            tp["Resource"]["Table"]["CatalogId"]
                        )
                    else:
                        allperms["Resource"].append("TableWithColumns")
                        allperms["Table_name"].append(
                            tp["Resource"]["TableWithColumns"]["Name"]
                        )
                        allperms["column_wild"].append("True")
                        allperms["catalog_id"].append(
                            tp["Resource"]["TableWithColumns"]["CatalogId"]
                        )

        # final_dict = {'permissions': allperms}
        new_data = [dict(zip(allperms.keys(), i)) for i in zip(*allperms.values())]
        result = [json.dumps(record) for record in new_data]

        filename = str(uuid.uuid4()) + ".json"

        resp = s3.put_object(
            Bucket=bucket,
            Key=f"{output_path}/{filename}",
            Body=bytes("\n".join(result).encode()),
        )
        allFiles.append(filename)

    write_file_list = s3.put_object(
        Bucket=bucket,
        Key=f"permissions_file_list.txt",
        Body=bytes("\n".join(allFiles).encode()),
    )
    LOGGER.info(write_file_list)

    return {
        "statusCode": 200,
        "body": json.dumps("Finished uploading permissions data!"),
    }


def clean_up(event, context):
    get_file_names = (
        s3.get_object(
            Bucket=bucket,
            Key="permissions_file_list.txt",
        )["Body"]
        .read()
        .decode()
        .split("\n")
    )

    delObj = []
    try:
        for obj in get_file_names:
            delObj.append({"Key": f"{output_path}/{obj}"})
        delInfo = s3.delete_objects(Bucket=bucket, Delete={"Objects": delObj})
    except:
        LOGGER.info("It appears there are no tables to clean up...")
    return delInfo
