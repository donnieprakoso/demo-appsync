#!/usr/bin/env python3
from constructs import Construct
from aws_cdk import aws_appsync as _as
from aws_cdk import aws_dynamodb as _ddb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as _iam
import aws_cdk as core
import os.path

class CdkStack(core.Stack):
    def __init__(self, scope: Construct, id: str, stack_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, "../graphql/schema.txt"), 'r') as file:
                    data_schema = file.read().replace('\n', '')
        with open(os.path.join(dirname, "../resolver_functions/create_character"), 'r') as file:
                    create_character = file.read().replace('\n', '')             
        with open(os.path.join(dirname, "../resolver_functions/update_character"), 'r') as file:
                    update_character = file.read().replace('\n', '')
        with open(os.path.join(dirname, "../resolver_functions/get_character"), 'r') as file:
                    get_character = file.read().replace('\n', '')   
        with open(os.path.join(dirname, "../resolver_functions/all_characters"), 'r') as file:
                    all_characters = file.read().replace('\n', '')   
        with open(os.path.join(dirname, "../resolver_functions/delete_character"), 'r') as file:
                    delete_character = file.read().replace('\n', '')   

        # The code that defines your stack goes here
        table_name = "{}-characters".format(stack_prefix)

        characters_graphql_api = _as.CfnGraphQLApi(
            self,'{}-charactersApi'.format(stack_prefix),
            name="{}-characters-api".format(stack_prefix),
            authentication_type='API_KEY'
        )
        
        graphql_api_key=_as.CfnApiKey(
            self,'{}-charactersApiKey'.format(stack_prefix),
            api_id = characters_graphql_api.attr_api_id

        )

        api_schema = _as.CfnGraphQLSchema(
            self,"{}-charactersSchema".format(stack_prefix),
            api_id = characters_graphql_api.attr_api_id,
            definition=data_schema
        )

        characters_table = _ddb.Table(
            self, '{}-charactersTable'.format(stack_prefix),
            table_name=table_name,
            partition_key=_ddb.Attribute(
                name='id',
                type=_ddb.AttributeType.STRING,

            ),        
            billing_mode=_ddb.BillingMode.PAY_PER_REQUEST,
            stream=_ddb.StreamViewType.NEW_IMAGE,
            removal_policy=core.RemovalPolicy.DESTROY 
        )

        characters_table_role = _iam.Role(
            self, '{}-charactersDynamoDBRole'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('appsync.amazonaws.com')
        )

        characters_table_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonDynamoDBFullAccess'
            )
        )

        data_source = _as.CfnDataSource(
            self, '{}-datasource'.format(stack_prefix),
            api_id=characters_graphql_api.attr_api_id,
            name='{}-datasource'.format(stack_prefix).replace('-', '_'),
            type='AMAZON_DYNAMODB',
            dynamo_db_config=_as.CfnDataSource.DynamoDBConfigProperty(
                table_name=characters_table.table_name,
                aws_region=self.region
            ),
            service_role_arn=characters_table_role.role_arn
        )

        get_character_resolver = _as.CfnResolver(
            self, '{}-GetOneQueryResolver'.format(stack_prefix),
            api_id=characters_graphql_api.attr_api_id,
            type_name='Query',
            field_name='getCharacter',
            data_source_name=data_source.name,
            request_mapping_template=get_character,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_character_resolver.add_depends_on(api_schema)

        get_all_characters_resolver = _as.CfnResolver(
            self, '{}-GetAllQueryResolver'.format(stack_prefix),
            api_id=characters_graphql_api.attr_api_id,
            type_name='Query',
            field_name='allCharacters',
            data_source_name=data_source.name,
            request_mapping_template=all_characters,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_all_characters_resolver.add_depends_on(api_schema)
     
        create_characters_resolver = _as.CfnResolver(
            self, '{}-CreateCharacterMutationResolver'.format(stack_prefix),
            api_id=characters_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='createCharacter',
            data_source_name=data_source.name,
            request_mapping_template=create_character,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        create_characters_resolver.add_depends_on(api_schema)

        update_characters_resolver = _as.CfnResolver(
            self,'{}-UpdateMutationResolver'.format(stack_prefix),
            api_id=characters_graphql_api.attr_api_id,
            type_name="Mutation",
            field_name="updateCharacter",
            data_source_name=data_source.name,
            request_mapping_template=update_character,
            response_mapping_template="$util.toJson($ctx.result)"
        )
        update_characters_resolver.add_depends_on(api_schema)

        delete_character_resolver = _as.CfnResolver(
            self, '{}-DeleteMutationResolver'.format(stack_prefix),
            api_id=characters_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='deleteCharacter',
            data_source_name=data_source.name,
            request_mapping_template=delete_character,
            response_mapping_template="$util.toJson($ctx.result)"
        )
        delete_character_resolver.add_depends_on(api_schema)

        core.CfnOutput(self,
                       "{}-out-appsync-url".format(stack_prefix),
                       value=characters_graphql_api.attr_graph_ql_url,
                       export_name="{}-appsync-url".format(stack_prefix))        

        core.CfnOutput(self,
                       "{}-out-appsync-key".format(stack_prefix),
                       value=graphql_api_key.attr_api_key,
                       export_name="{}-appsync-key".format(stack_prefix))        

stack_prefix = 'appsync-1'
app = core.App()
stack = CdkStack(app, stack_prefix, stack_prefix=stack_prefix)
core.Tags.of(stack).add('Name', stack_prefix)

app.synth()
