import json
import boto3
import os

glue_client = boto3.client('glue')
s3_client = boto3.client('s3')

# Pegue as variáveis de ambiente fora do handler
GLUE_JOB_NAME = os.environ.get('GLUE_JOB_NAME')
IDEMPOTENCY_BUCKET = os.environ.get('IDEMPOTENCY_BUCKET_NAME')
DATA_BUCKET_OUTPUT = os.environ.get('DATA_BUCKET_OUTPUT')
print("Variáveis de ambiente carregadas:", os.environ)

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
        print(record)
        try:
            sqs_body = json.loads(record['body'])
            sns_message_str = sqs_body.get('Message')
            
            if not sns_message_str:
                print(f"Aviso: Mensagem SNS não encontrada. Pular.")
                continue
            if isinstance(sns_message_str, str):
                sns_message = json.loads(sns_message_str)
            else:
                # Se ja for um objeto (dict), use-o diretamente
                sns_message = sns_message_str
            
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
            if 'message' in sns_message and isinstance(sns_message['message'], dict):
                inner_message = sns_message['message']
            else:
                # Se a mensagem ja nao for aninhada, use-a diretamente (para ser retrocompativel)
                inner_message = sns_message
            print("Conteúdo da Mensagem do SNS:", sns_message) 
            args_glue = {
                '--ano': inner_message.get('ano'),
                '--mes': inner_message.get('mes'),
                '--dia': inner_message.get('dia'),
                '--data_bucket_name_output': DATA_BUCKET_OUTPUT,
            }
            
            if not all(args_glue.values()):
                raise ValueError("Payload do SNS não contém todos os argumentos necessários.")
            
            print(f"Iniciando job Glue '{GLUE_JOB_NAME}' com os argumentos: {json.dumps(args_glue)}")
            
            response = glue_client.start_job_run(
                JobName=GLUE_JOB_NAME,
                Arguments=args_glue
            )

            print(f"Resposta do Glue: {response}")
            
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