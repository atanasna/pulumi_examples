import pulumi_aws as aws
import zipfile
from lib.helpers import jinja_to_json

def example_1(iac_admin_ropts):
    zipfile.ZipFile('lambda.zip', mode='w').write("scripts/example_1/handler.rb")
    
    lambda_role_assumer_policy = jinja_to_json(
        template_path = 'policies/example_1/lambda_role_assumer.j2',
        data = {
            "lambda_service":"lambda.amazonaws.com"
        })

    lambda_role_operator_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"

    lambda_role = aws.iam.Role("lambda_role_t1", 
        assume_role_policy = lambda_role_assumer_policy, 
        opts = iac_admin_ropts)

    lambda_role_attachment = aws.iam.RolePolicyAttachment("ex1_lambda_policy_attach",
        policy_arn = lambda_role_operator_policy_arn,
        role = lambda_role.name,
        opts = iac_admin_ropts)

    lambda_function = aws.lambda_.Function("ruby_function", 
        handler = "lambda_handler",
        runtime = "ruby2.5",
        code = "lambda.zip",
        role = lambda_role.arn,
        opts = iac_admin_ropts)