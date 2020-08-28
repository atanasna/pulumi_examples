import pulumi_aws as aws
import zipfile
import shutil
import os
import pulumi
from lib.helpers import jinja_to_json
from lib.helpers import jinja_to_txt

def sm_syncer(iac_admin_ropts, remote_region, sync_exceptions):

    region = aws.get_region(opts=iac_admin_ropts).name
    sync_lambda = create_sync_lambda(iac_admin_ropts, remote_region, sync_exceptions)

    # Create the EventBridge Rule
    rule = aws.cloudwatch.EventRule(f"secret_syncer_{region}",
        description="Capture each SecretsManager value change",
        event_pattern=jinja_to_txt(
            template_path = f"{os.path.dirname(__file__)}/policies/event_pattern.j2",
            data = {}),
        opts = iac_admin_ropts)
    
    #aws_logins = aws.sns.Topic("awsLogins")

    target = aws.cloudwatch.EventTarget(f"secret_lambda_{region}",
        rule = rule.name,
        arn = sync_lambda.arn,
        opts = iac_admin_ropts)
    
    aws.lambda_.Permission(f"allow_eventbridge_{region}",
        action="lambda:InvokeFunction",
        function=sync_lambda.name,
        principal="events.amazonaws.com",
        source_arn=rule.arn,
        opts = iac_admin_ropts)

def create_sync_lambda(iac_admin_ropts, remote_region, sync_exceptions):
    region = aws.get_region(opts=iac_admin_ropts).name
    # Create the lambda that will sync the secrets
    shutil.make_archive("lambda_ex2", 'zip', f"{os.path.dirname(__file__)}/scripts")

    lambda_role_assumer_policy = jinja_to_json(
        template_path = f"{os.path.dirname(__file__)}/policies/lambda_role_assumer.j2",
        data = {
            "lambda_service":"lambda.amazonaws.com"
        })

    lambda_role_operator_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"

    lambda_role = aws.iam.Role(f"lambda_role_pulumi_example_2_{region}", 
        assume_role_policy = lambda_role_assumer_policy, 
        opts = iac_admin_ropts)

    lambda_role_attachment = aws.iam.RolePolicyAttachment(f"ex2_lambda_policy_attach_{region}",
        policy_arn = lambda_role_operator_policy_arn,
        role = lambda_role.name,
        opts = iac_admin_ropts)

    lambda_function = aws.lambda_.Function(f"pulumi_example_2_py_{region}", 
        handler = "sm_syncer.main",
        runtime = "python3.6",
        code = "lambda_ex2.zip",
        environment = {
            "variables":{
                "remote_region": remote_region,
                "exceptions": ",".join(sync_exceptions)
            }
        },
        tags = {"alabala":"protokala"},
        role = lambda_role.arn,
        opts = iac_admin_ropts)

    return lambda_function
