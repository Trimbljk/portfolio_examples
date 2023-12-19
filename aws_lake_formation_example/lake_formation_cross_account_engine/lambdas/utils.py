import datetime as dt
import uuid
import boto3
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

baseRoles = {
    "admin": "arn:aws:iam:::role/aws-reserved/sso.amazonaws.com/us-west-2/AWSReservedSSO_AdministratorAccess_f84d5a078952424c",
    "org": "arn:aws:organizations:::organization/",
}


class EventSorter:
    def __init__(self, eventList):
        self.eventList = eventList

    def attributes(self):
        attributes = []
        for e in self.eventList:
            event = e["detail"]
            try:
                if event["errorCode"]:
                    LOGGER.info(
                        f"There was an error in the event: {event['errorCode'], event['errorMessage']}"
                    )
                    continue
            except:
                LOGGER.info("No event errors detected, adding to sort...")

            attr = {
                "eventName": event["eventName"],
                "databaseName": event["requestParameters"]["databaseName"],
                "eventTime": self.parseTime(event["eventTime"]),
                "eventId": e["id"],
            }

            if event["eventName"] == "DeleteTable":
                attr["tableName"] = event["requestParameters"]["name"]
                attr["storageLocation"] = ""

            elif event["eventName"] in ["CreateTable", "UpdateTable"]:
                attr["tableName"] = event["requestParameters"]["tableInput"]["name"]
                attr["storageLocation"] = event["requestParameters"]["tableInput"][
                try:
                    LOGGER.info("Checking table type...")
                    attr["tableType"] = event["requestParameters"]["tableInput"][
                        "tableType"
                    ].lower()
                except:
                    attr["tableType"] = "table"

            attributes.append(attr)

        return attributes

    def parseTime(self, dateElement):
        return dt.datetime.strptime(dateElement, "%Y-%m-%dT%H:%M:%SZ").timestamp()

    def table_queues(self):
        databases = {}
        for e in self.attributes():
            if e["databaseName"] in databases.keys():
                if e["tableName"] in databases[e["databaseName"]].keys():
                    databases[e["databaseName"]][e["tableName"]].append(e)
                else:
                    databases[e["databaseName"]][e["tableName"]] = []
                    databases[e["databaseName"]][e["tableName"]].append(e)
            else:
                databases[e["databaseName"]] = {}
                databases[e["databaseName"]][e["tableName"]] = []
                databases[e["databaseName"]][e["tableName"]].append(e)
        tableEventQueues = {"CreateTable": [], "DeleteTable": [], "UpdateTable": []}
        for database, table in databases.items():
            for tab, event in table.items():
                sortedList = sorted(event, key=lambda d: d["eventTime"], reverse=True)
                LOGGER.info(f"SORTED LIST: {sortedList}")
                try:
                    if sortedList[0]["eventName"] == "UpdateTable":
                        get_path = sortedList[0]["storageLocation"]
                        for etype in sortedList:
                            LOGGER.info(etype)
                            if etype["eventName"] == "CreateTable":
                                moveToFront = etype
                            else:
                                pass
                        sortedList.insert(0, moveToFront)
                        sortedList[0]["storageLocation"] = get_path
                    else:
                        pass
                except:
                    LOGGER.info("List editing not applicable...")
                tableEventQueues[sortedList[0]["eventName"]].append(sortedList[0])
        return tableEventQueues


class PermissionsObject:
    def __init__(self, database, table, arn, perms, grants=None):
        self.database = database
        self.table = table
        self.arn = arn
        self.perms = perms
        self.grants = grants

    def add(self):
        permissions = {
            "Id": str(uuid.uuid4()),
            "Principal": {"DataLakePrincipalIdentifier": self.arn},
            "Resource": {"Table": {"DatabaseName": self.database, "Name": self.table}},
            "Permissions": self.perms,
        }
        if self.grants != None:
            permissions["PermissionsWithGrantOption"] = self.grants

        return permissions


class DeleteActions:
    athena = boto3.client("athena")

    def __init__(self, database, table):
        self.database = database
        self.table = table

    def run_queries(self, query_selector="all"):
        glueTablePrefix = """arn:aws:glue:us-west-2::table/"""
        self.searchString = glueTablePrefix + self.database + "/" + self.table
        associationQuery = f"SELECT associated_entity, arn FROM lakeformation.resource_shares WHERE associated_entity = '{self.searchString}'"
        permissionQuery = f"SELECT * FROM lakeformation.lakeformation_permissions WHERE table_name = '{self.table}' AND database_name ='{self.database}'"
        s3LocationQuery = f"SELECT * FROM lakeformation.table_location_paths WHERE table_name = '{self.table}' AND database_name = '{self.database}'"
        queryInfo = {
            "association": associationQuery,
            "permissions": permissionQuery,
            "location": s3LocationQuery,
        }
        if query_selector == "all":
            queries = queryInfo
        else:
            if isinstance(query_selector, list):
                queries = {}
                for i in query_selector:
                    queries[i] = queryInfo[i]

        self.queryIds = {}
        for action, query in queries.items():
            athena_resp = self.athena.start_query_execution(
                QueryString=query,
                ResultConfiguration={
                    "OutputLocation": "s3://aws-athena-query-results--us-west-2/"
                },
            )["QueryExecutionId"]
            self.queryIds[action] = athena_resp

        return self

    def show(self):
        return self.queryIds

    def status(self):
        status_info = []
        for query in self.queryIds.values():
            status = self.athena.get_query_execution(QueryExecutionId=query)[
                "QueryExecution"
            ]["Status"]["State"]
            status_info.append(status)

        return status_info

    def build_permission_state(self):
        response = self.athena.get_query_results(
            QueryExecutionId=self.queryIds["permissions"]
        )
        result = response["ResultSet"]["Rows"]
        colheads = result[0]["Data"]
        tableData = result[1::]

        item = {
            "tableName": self.table,
            "databaseName": self.database,
            "permissions": [],
        }

        key_list = ["arn", "permissions", "grants"]
        inv_map = {v: k for d in colheads for k, v in d.items()}

        keymap = {}
        for i, d in enumerate(inv_map.keys()):
            if d in key_list:
                keymap[i] = d
        LOGGER.info(keymap)

        for i in tableData:
            permissions_set = {}
            for e, d in enumerate(i["Data"]):
                if e in list(keymap.keys()):
                    if keymap[e] in ["permissions", "grants"]:
                        if list(d.values())[0] == "[]":
                            LOGGER.info("passing on empty list")
                        else:
                            res = str(list(d.values())[0]).strip("][").split(", ")
                            LOGGER.info(res)
                            permissions_set[keymap[e]] = list(res)
                    else:
                        permissions_set[keymap[e]] = list(d.values())[0]
            item["permissions"].append(permissions_set)

        return item

    def get_table_path(self):
        results = {}
        dataset = {}
        response = self.athena.get_query_results(
            QueryExecutionId=self.queryIds["location"]
        )

        for column in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]:
            dataset[column["Name"]] = []
        for row in response["ResultSet"]["Rows"]:
            for i, data in enumerate(row["Data"]):
                if data["VarCharValue"] in list(dataset.keys()):
                    results[i] = data["VarCharValue"]
                else:
                    dataset[results[i]].append(data["VarCharValue"])

        LOGGER.info(response)
        if "NextToken" in response:
            cont_token = response["NextToken"]
        while "NextToken" in response.keys():
            LOGGER.info("More data available... applying token")
            response = athena.get_query_results(
                QueryExecutionId=query, NextToken=cont_token
            )
            LOGGER.info(response)
            if "NextToken" in response.keys():
                cont_token = response["NextToken"]

            for column in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]:
                if column["Name"] in dataset.keys():
                    LOGGER.info("column already accounted for...")
                else:
                    dataset[column["Name"]] = []

            for row in response["ResultSet"]["Rows"]:
                LOGGER.info(row)
                for i, data in enumerate(row["Data"]):
                    if data["VarCharValue"] in list(dataset.keys()):
                        results[i] = data["VarCharValue"]
                    else:
                        dataset[results[i]].append(data["VarCharValue"])

        new_data = [dict(zip(dataset.keys(), i)) for i in zip(*dataset.values())][0]
        path = new_data["table_location_path"].replace("s3://", "arn:aws:s3:::")
        return path

    def get_share(self):
        response = self.athena.get_query_results(
            QueryExecutionId=self.queryIds["association"]
        )
        return (
            response["ResultSet"]["Rows"][1]["Data"][1]["VarCharValue"],
            self.searchString,
        )
