import json

def handler(event, context):
    """
    Função Lambda de exemplo para processar eventos do SNS ou SQS.
    """
    print("Evento recebido:")
    print(json.dumps(event))

    if 'Records' in event:
        for record in event['Records']:
            if record.get('Sns'):
                message = record['Sns']['Message']
                print(f"Mensagem do SNS: {message}")
            elif record.get('body'):
                message = record['body']
                print(f"Mensagem do SQS: {message}")

    return {
        'statusCode': 200,
        'body': json.dumps('Mensagem processada com sucesso!')
    }