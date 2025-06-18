# Ejemplo de integración Webpay usando el SDK oficial de Transbank para Python
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WebpaySDKService:
    def __init__(self):
        # Configurar credenciales según el ambiente
        if settings.WEBPAY_ENVIRONMENT == 'TEST':
            # Usar configuración de integración para testing
            self.tx = Transaction.build_for_integration(
                commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
                api_key=IntegrationApiKeys.WEBPAY
            )
        else:
            # Usar configuración de producción
            self.tx = Transaction.build_for_production(
                commerce_code=settings.WEBPAY_COMMERCE_CODE,
                api_key=settings.WEBPAY_API_KEY
            )
    
    def crear_transaccion(self, orden_compra, session_id, monto, url_retorno):
        try:
            response = self.tx.create(
                buy_order=orden_compra,
                session_id=session_id,
                amount=int(monto),
                return_url=url_retorno
            )
            logger.info(f"Transacción creada con SDK: {response}")
            return {
                'success': True,
                'token': response['token'],
                'url': response['url']
            }
        except Exception as e:
            logger.error(f"Error al crear transacción con SDK: {str(e)}")
            return {'success': False, 'error': str(e)}

    def confirmar_transaccion(self, token):
        try:
            result = self.tx.commit(token)
            logger.info(f"Resultado de confirmación SDK: {result}")
            return {
                'success': True,
                'vci': result.get('vci', ''),
                'amount': result.get('amount', 0),
                'status': result.get('status', ''),
                'buy_order': result.get('buy_order', ''),
                'session_id': result.get('session_id', ''),
                'card_detail': result.get('card_detail', {}),
                'accounting_date': result.get('accounting_date', ''),
                'transaction_date': result.get('transaction_date', ''),
                'authorization_code': result.get('authorization_code', ''),
                'payment_type_code': result.get('payment_type_code', ''),
                'response_code': result.get('response_code', -1),
                'installments_number': result.get('installments_number', 0)
            }
        except Exception as e:
            logger.error(f"Error al confirmar transacción con SDK: {str(e)}")
            return {'success': False, 'error': str(e)}
