#"""An AWS Python Pulumi program"""

#import aws from "@pulumi/aws";
#import pulumi from "@pulumi/pulumi";
import os
import json
import zipfile
import pulumi
from lambdata import create_the_lambda
from jinja2 import Template
import pulumi_aws as aws
from lib.helpers import jinja_to_json
#from pulumi_aws import s3

iac_admin_sbx = aws.Provider("roler", assume_role = {
    "roleArn" : "arn:aws:iam::415099068017:role/iac-admin-role",
    "sessionName" : "PulumiSession",
    "externalId" : "PulumiApplication"},
    region = "us-east-1"
)
iac_admin_ropts = pulumi.ResourceOptions(provider = iac_admin_sbx)

zipfile.ZipFile('lambda.zip', mode='w').write("scripts/test1/handler.rb")

create_the_lambda(iac_admin_ropts)

bucket = aws.s3.Bucket('bobri', opts=iac_admin_ropts)
#pulumi.export('bucket_name', bucket.id)

