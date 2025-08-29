import json

def handler(event, context):
    """
    Função Lambda que processa um evento do SQS, decodifica a mensagem SNS
    e imprime os atributos e o corpo da mensagem.
    """
    print("--- Evento completo recebido da Lambda ---")
    print(json.dumps(event, indent=2))
    print("--- Fim do evento ---")

    if 'Records' in event:
        # Itera sobre cada mensagem (record) na lista de eventos do SQS
        for record in event['Records']:
            # O corpo da mensagem do SQS é uma string JSON que contém o evento do SNS
            try:
                # Decodifica o corpo da mensagem SQS para um objeto Python
                sqs_body = json.loads(record.get('body', '{}'))
                
                # O corpo do SQS contém o evento SNS, que é outra string JSON
                sns_message_str = sqs_body.get('Message')

                if sns_message_str:
                    # Decodifica a string da mensagem do SNS para um objeto Python
                    sns_message = json.loads(sns_message_str)

                    # Extrai os atributos da mensagem
                    message_attributes = sqs_body.get('MessageAttributes', {})
                    
                    # Extrai o payload principal da mensagem
                    payload_principal = sns_message

                    print("\n--- Atributos da Mensagem ---")
                    for attr_name, attr_value in message_attributes.items():
                        print(f"Atributo: {attr_name}, Valor: {attr_value.get('Value')}")
                    
                    print("\n--- Payload Principal da Mensagem ---")
                    print(json.dumps(payload_principal, indent=2))
                
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e}")
                print(f"Corpo da mensagem recebida: {record.get('body')}")
            
    return {
        'statusCode': 200,
        'body': json.dumps('Mensagem processada com sucesso!')
    }