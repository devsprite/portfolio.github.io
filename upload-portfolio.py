import boto3
import zipfile
import StringIO
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:022026396507:deployPortfolioTopic')
    
    try:
        s3 = boto3.resource('s3')
        
        build_bucket = s3.Bucket('portfolio.build.chez-dominique.fr')
        portfolio_bucket = s3.Bucket('portfolio.chez-dominique.fr')
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
    
        print 'Job done!'
        topic.publish(Subject="Portfolio Deployed", Message="Job done!")
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="The portfolio was not deployed successfully!")
        raise
    