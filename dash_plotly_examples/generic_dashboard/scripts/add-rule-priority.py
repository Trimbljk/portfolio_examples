#!/usr/bin/env python

import json

import boto3
import click
from cfn_flip import to_json, to_yaml

CLUSTER_STACK_NAME = "AgbiomeFargateClusterStack"


def set_priority(template, priority):
    template["Resources"]["LoadBalancerRule"]["Properties"][
        "Priority"
    ] = priority
    yaml = to_yaml(json.dumps(template))
    return yaml


def load_template(template_fp):
    with open(template_fp, "r") as fh:
        template = to_json(fh.read())
    template = json.loads(template)
    return template


def get_highest_priority(listener_arn):
    elbv2 = boto3.client("elbv2")
    rules = elbv2.describe_rules(ListenerArn=listener_arn)
    priorities = [
        int(d["Priority"]) if d["Priority"] != "default" else 0
        for d in rules["Rules"]
    ]
    return max(priorities)


def get_listener_arn(resources):
    for resource in resources:
        if resource["LogicalResourceId"] == "LoadBalancerListener":
            return resource["PhysicalResourceId"]


def get_existing_rule_priority(listener_rule_arn):
    elbv2 = boto3.client("elbv2")
    rules = elbv2.describe_rules(RuleArns=[listener_rule_arn])
    return rules["Rules"][0]["Priority"]


def get_stack_resources(stack_name):
    cf_resource = boto3.resource("cloudformation")
    states = ["ROLLBACK_COMPLETE", "CREATE_COMPLETE", "UPDATE_COMPLETE"]
    stacks = [
        i.stack_name
        for i in cf_resource.stacks.all()
        if i.stack_status in states
    ]

    if stack_name not in stacks:
        return None

    cf_client = boto3.client("cloudformation")
    resources = cf_client.describe_stack_resources(StackName=stack_name)
    return resources["StackResources"]


def get_listener_rule(resources):
    for resource in resources:
        if resource["LogicalResourceId"] == "LoadBalancerRule":
            return resource["PhysicalResourceId"]
    return None


@click.command()
@click.argument("stack_name")
@click.argument("template_fp")
def main(stack_name, template_fp):
    stack_resources = get_stack_resources(stack_name)

    priority = None
    if stack_resources:
        listener_rule_arn = get_listener_rule(stack_resources)
        if listener_rule_arn:
            priority = get_existing_rule_priority(listener_rule_arn)

    if priority is None:
        cluster_resources = get_stack_resources(CLUSTER_STACK_NAME)
        listener_arn = get_listener_arn(cluster_resources)
        priority = get_highest_priority(listener_arn) + 1

    template = load_template(template_fp)
    click.echo(set_priority(template, priority=priority))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
