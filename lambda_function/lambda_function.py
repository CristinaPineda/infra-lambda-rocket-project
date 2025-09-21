import json
import boto3
import os

glue_client = boto3.client('glue')
s3_client = boto3.client('s3')

# Pegue as variáveis de ambiente fora do handler
GLUE_JOB_NAME = os.environ.get('GLUE_JOB_NAME')
IDEMPOTENCY_BUCKET = os.environ.get('IDEMPOTENCY_BUCKET_NAME')
DATA_BUCKET_OUTPUT = os.environ.get('DATA_BUCKET_OUTPUT')

def handler(event, context):
    """
    Função Lambda que processa um evento do SQS/SNS, garante a idempotência
    e inicia um job Glue.
    """
    if 'Records' not in event:
        print(event)
        print("Aviso: O evento não contém registros SQS. Encerrando.")
        return {'statusCode': 200}

    for record in event['Records']:
        try:
            sqs_body = json.loads(record['body'])
            sns_message_str = sqs_body.get('Message')
            
            if not sns_message_str:
                print(f"Aviso: Mensagem SNS não encontrada. Pular.")
                continue
            
            # --- Lógica de Idempotência ---
            message_id = record.get('messageId')

            if not message_id:
                print(f"Aviso: MessageId não encontrado no registro. Pular.")
                continue

            # 1. Tente encontrar o arquivo de ID no bucket de idempotência
            try:
                s3_client.head_object(Bucket=IDEMPOTENCY_BUCKET, Key=message_id)
                print(f"Idempotência: ID da mensagem '{message_id}' já processado. Encerrando o job.")
                continue  # Pula para a próxima mensagem no lote
            except s3_client.exceptions.ClientError as e:
                # O erro 404 significa que o objeto não foi encontrado, o que é o esperado
                if e.response['Error']['Code'] == '404':
                    print(f"Idempotência: ID da mensagem '{message_id}' não encontrado. Iniciando o processamento.")
                    
                    # 2. Crie um arquivo para marcar o ID como "em processamento"
                    s3_client.put_object(Bucket=IDEMPOTENCY_BUCKET, Key=message_id, Body=b'')
                else:
                    # Se for outro erro do S3, levanta a exceção
                    raise e

            # --- Lógica para Iniciar o Job Glue ---
            sns_message = json.loads(sns_message_str)
            args_glue = {
                '--ano': sns_message.get('ano'),
                '--mes': sns_message.get('mes'),
                '--dia': sns_message.get('dia'),
                '--data_bucket_name_output': DATA_BUCKET_OUTPUT,
            }
            
            if not all(args_glue.values()):
                raise ValueError("Payload do SNS não contém todos os argumentos necessários.")
            
            print(f"Iniciando job Glue '{GLUE_JOB_NAME}' com os argumentos: {json.dumps(args_glue)}")
            
            response = glue_client.start_job_run(
                JobName=GLUE_JOB_NAME,
                Arguments=args_glue
            )
            
            print(f"Job Glue iniciado com sucesso. Run ID: {response['JobRunId']}")
            
        except json.JSONDecodeError as e:
            print(f"ERRO DE DECODIFICAÇÃO DE JSON: {e}")
            raise e
        except ValueError as e:
            print(f"ERRO DE VALIDAÇÃO: {e}")
            raise e
        except Exception as e:
            print(f"ERRO INESPERADO: {e}")
            raise e
            
    return {
        'statusCode': 200,
        'body': json.dumps('Mensagens processadas e jobs iniciados com sucesso.')
    }