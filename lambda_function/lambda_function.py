import json
import boto3
import os
import logging

# --- Configuração do Logger ---
# Configura o logger para a função Lambda.
# Recomenda-se o nível INFO em produção para logs importantes.
# Altere para DEBUG se precisar de mais detalhes durante o desenvolvimento/troubleshooting.
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Nível padrão

# Inicialização de Clientes AWS (Melhor manter fora do handler para reutilização a quente)
try:
    glue_client = boto3.client('glue')
    s3_client = boto3.client('s3')
    logger.info("Clientes AWS 'glue' e 's3' inicializados.")
except Exception as e:
    logger.error(f"ERRO: Falha ao inicializar clientes AWS. {e}")
    # Dependendo do seu ambiente, você pode querer levantar a exceção
    # ou deixar o erro ser tratado na primeira execução do handler.

# Pegue as variáveis de ambiente fora do handler
GLUE_JOB_NAME = os.environ.get('GLUE_JOB_NAME')
IDEMPOTENCY_BUCKET = os.environ.get('IDEMPOTENCY_BUCKET_NAME')
DATA_BUCKET_OUTPUT = os.environ.get('DATA_BUCKET_OUTPUT')

if not all([GLUE_JOB_NAME, IDEMPOTENCY_BUCKET, DATA_BUCKET_OUTPUT]):
    logger.critical("ERRO CRÍTICO: Uma ou mais variáveis de ambiente necessárias não estão configuradas.")
    # Em um ambiente de produção, isso geralmente causaria uma falha na implantação/inicialização
    
logger.info(f"Variáveis de ambiente carregadas: GLUE_JOB_NAME={GLUE_JOB_NAME}, IDEMPOTENCY_BUCKET={IDEMPOTENCY_BUCKET}, DATA_BUCKET_OUTPUT={DATA_BUCKET_OUTPUT}")


def handler(event, context):
    """
    Função Lambda que processa um evento do SQS/SNS, garante a idempotência
    e inicia um job Glue.
    """
    # Adiciona o ID da requisição do Lambda para rastreamento no log.
    logger.info(f"--- Início da execução da Lambda. Request ID: {context.aws_request_id} ---")
    
    if 'Records' not in event:
        logger.warning(f"O evento não contém registros SQS. Conteúdo do evento: {event}")
        logger.info("Encerrando a função com sucesso (statusCode: 200).")
        return {'statusCode': 200}

    # Log do total de registros recebidos
    num_records = len(event['Records'])
    logger.info(f"Recebidos {num_records} registro(s) para processamento.")

    for i, record in enumerate(event['Records']):
        log_prefix = f"[Registro {i+1}/{num_records}]"
        logger.debug(f"{log_prefix} Detalhes do registro SQS: {record}") # DEBUG: log detalhado do SQS
        
        try:
            # Tenta decodificar o corpo do SQS
            sqs_body = json.loads(record['body'])
            sns_message_str = sqs_body.get('Message')
            
            if not sns_message_str:
                logger.warning(f"{log_prefix} Mensagem SNS não encontrada ('Message' vazio/nulo no corpo do SQS). Pulando para o próximo registro.")
                continue
            
            # Tenta decodificar a mensagem do SNS
            if isinstance(sns_message_str, str):
                sns_message = json.loads(sns_message_str)
            else:
                # Se ja for um objeto (dict), usa-o diretamente (caminho menos comum)
                sns_message = sns_message_str
            
            # --- Lógica de Idempotência ---
            message_id = record.get('messageId')

            if not message_id:
                logger.warning(f"{log_prefix} MessageId não encontrado no registro SQS. Impossível garantir a idempotência. Pulando.")
                continue
            
            # 1. Tente encontrar o arquivo de ID no bucket de idempotência
            try:
                s3_client.head_object(Bucket=IDEMPOTENCY_BUCKET, Key=message_id)
                # Objeto encontrado: Mensagem já processada
                logger.info(f"{log_prefix} ID da mensagem '{message_id}' JÁ PROCESSADO. Encerrando o processamento deste registro (Idempotência).")
                continue  # Pula para a próxima mensagem no lote (Idempotência)
            except s3_client.exceptions.ClientError as e:
                # O erro 404 significa que o objeto não foi encontrado
                if e.response['Error']['Code'] == '404':
                    logger.info(f"{log_prefix} ID da mensagem '{message_id}' NÃO ENCONTRADO. Iniciando processamento e marcando como 'em processamento'.")
                    
                    # 2. Crie um arquivo para marcar o ID como "em processamento"
                    s3_client.put_object(Bucket=IDEMPOTENCY_BUCKET, Key=message_id, Body=b'')
                    logger.debug(f"{log_prefix} Objeto de idempotência '{message_id}' criado com sucesso.")
                else:
                    # Se for outro erro do S3, levanta a exceção
                    logger.error(f"{log_prefix} ERRO INESPERADO DO S3 durante a verificação de idempotência para '{message_id}'. Erro: {e}", exc_info=True)
                    raise e

            # --- Lógica para Iniciar o Job Glue ---
            
            # Pega a mensagem interna que contém os parâmetros do Glue
            if 'message' in sns_message and isinstance(sns_message['message'], dict):
                inner_message = sns_message['message']
            else:
                # Se a mensagem já não for aninhada, usa-a diretamente
                inner_message = sns_message
            
            logger.info(f"{log_prefix} Conteúdo da Mensagem do SNS processada: {inner_message}") 
            
            args_glue = {
                '--ano': inner_message.get('ano'),
                '--mes': inner_message.get('mes'),
                '--dia': inner_message.get('dia'),
                '--data_bucket_name_output': DATA_BUCKET_OUTPUT,
            }
            
            # Validação dos argumentos
            if not all(args_glue.values()):
                missing_args = [k for k, v in args_glue.items() if v is None]
                raise ValueError(f"Payload do SNS não contém todos os argumentos necessários. Argumentos ausentes: {', '.join(missing_args)}")
            
            logger.info(f"{log_prefix} Iniciando job Glue '{GLUE_JOB_NAME}' com os argumentos: {json.dumps(args_glue)}")
            
            response = glue_client.start_job_run(
                JobName=GLUE_JOB_NAME,
                Arguments=args_glue
            )

            logger.debug(f"{log_prefix} Resposta bruta do Glue: {response}")
            
            logger.info(f"{log_prefix} Job Glue iniciado com sucesso. Run ID: {response['JobRunId']}")
            
        except json.JSONDecodeError as e:
            # ERRO: Falha ao decodificar JSON (SQS Body ou SNS Message)
            logger.error(f"{log_prefix} ERRO DE DECODIFICAÇÃO DE JSON. Verifique o formato da mensagem. Erro: {e}", exc_info=True)
            # Re-lançar exceção para falhar o lote SQS, se configurado
            raise e 
        except ValueError as e:
            # ERRO: Falha na validação de dados
            logger.error(f"{log_prefix} ERRO DE VALIDAÇÃO: Falha nos dados de entrada. Erro: {e}", exc_info=True)
            # Re-lançar exceção para falhar o lote SQS, se configurado
            raise e
        except Exception as e:
            # ERRO: Qualquer outra exceção
            logger.error(f"{log_prefix} ERRO INESPERADO durante o processamento do registro. Erro: {e}", exc_info=True)
            # Re-lançar exceção para falhar o lote SQS, se configurado
            raise e
            
    logger.info("--- Processamento de todos os registros concluído. ---")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Mensagens processadas e jobs iniciados com sucesso.')
    }