#"""An AWS Python Pulumi program"""

#import aws from "@pulumi/aws";
#import pulumi from "@pulumi/pulumi";
import os
import json
import zipfile
import pulumi

from jinja2 import Template
import pulumi_aws as aws

from lib.helpers import jinja_to_json

from example_1_lambda import example_1
from example_2_sm_syncer.main import sm_syncer

#from pulumi_aws import s3

iac_admin_r1_sbx = aws.Provider("roler1", assume_role = {
    "roleArn" : "arn:aws:iam::415099068017:role/iac-admin-role",
    "sessionName" : "PulumiSessionRegion1",
    "externalId" : "PulumiApplication"},
    region = "us-east-1"
)
iac_admin_r2_sbx = aws.Provider("roler2", assume_role = {
    "roleArn" : "arn:aws:iam::415099068017:role/iac-admin-role",
    "sessionName" : "PulumiSessionRegion2",
    "externalId" : "PulumiApplication"},
    region = "us-east-2"
)

iac_admin_r1_ropts = pulumi.ResourceOptions(provider = iac_admin_r1_sbx)
iac_admin_r2_ropts = pulumi.ResourceOptions(provider = iac_admin_r2_sbx)


example_1(iac_admin_r1_ropts)

# EXAMPLE 2
sm_syncer(iac_admin_r1_ropts, remote_region="us-east-2", sync_exceptions=["sync_ex1", "sync_ex2"])
sm_syncer(iac_admin_r2_ropts, remote_region="us-east-1", sync_exceptions=["sync_ex1", "sync_ex2"])

#bucket = aws.s3.Bucket('bobri', opts=iac_admin_ropts)
#pulumi.export('bucket_name', bucket.id)

