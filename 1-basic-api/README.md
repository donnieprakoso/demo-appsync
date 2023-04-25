## GraphQL with AWS AppSync

This is a repository for GraphQL demo using Star Wars dataset from [fgeorges/star-wars-dataset](https://github.com/fgeorges/star-wars-dataset/) repository. 

### How to Deploy?

To ensure smooth deployment, make sure that you have AWS CDK v2 and Python3 (preferably with venv) installed.

1. Go to `cdk` folder. 
2. Run `pip install -r requirements`
3. Run `cdk deploy` and follow the instructions
4. Upon completion, you will have two outputs:
```
appsync-1.appsync1outappsynckey = XYZ
appsync-1.appsync1outappsyncurl = XYZ
```
At this stage, you have your AppSync with DynamoDB as data source along with 5 resolvers. 

### How to load initial data?

1. Export each output as environment variable:
```
export GRAPHQL_URL=XYZ
export GRAPHQL_API_KEY=XYZ
```
2. Go to `data/`
3. Run `pip install -r requirements`
4. Run `python app.py` — This will download data from the dataset source, and load them into DynamoDB via GraphQL mutation.

### How to test?

You can test the GraphQL and do queries by visiting [AppSync console](https://console.aws.amazon.com/appsync/).

Happy building!
— D