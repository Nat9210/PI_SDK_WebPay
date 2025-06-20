from django.core.management.base import BaseCommand
from pagos.models import Transaccion
import random

class Command(BaseCommand):
    help = 'Configura estados de pedido para las transacciones existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reinicia todos los estados a PENDIENTE_REVISION',
        )
        parser.add_argument(
            '--diversificar',
            action='store_true',
            help='Diversifica los estados para demo',
        )

    def handle(self, *args, **options):
        transacciones = Transaccion.objects.filter(estado='AUTORIZADA')
        
        if options['reset']:
            # Reiniciar todos a pendiente
            updated = transacciones.update(estado_pedido='PENDIENTE_REVISION')
            self.stdout.write(
                self.style.SUCCESS(f'✅ {updated} transacciones reiniciadas a PENDIENTE_REVISION')
            )
            
        elif options['diversificar']:
            # Diversificar estados para demo
            estados = [
                'PENDIENTE_REVISION',
                'ACEPTADO', 
                'RECHAZADO',
                'EN_PREPARACION',
                'ENVIADO',
                'ENTREGADO'
            ]
            
            for transaccion in transacciones:
                # Asignar estado aleatorio pero con mayor probabilidad para ciertos estados
                if random.random() < 0.3:  # 30% pendiente
                    estado = 'PENDIENTE_REVISION'
                elif random.random() < 0.4:  # 40% aceptado
                    estado = 'ACEPTADO'
                elif random.random() < 0.1:  # 10% rechazado
                    estado = 'RECHAZADO'
                elif random.random() < 0.1:  # 10% preparación
                    estado = 'EN_PREPARACION'
                elif random.random() < 0.05:  # 5% enviado
                    estado = 'ENVIADO'
                else:  # 5% entregado
                    estado = 'ENTREGADO'
                
                transaccion.estado_pedido = estado
                transaccion.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {transacciones.count()} transacciones diversificadas')
            )
            
            # Mostrar estadísticas
            stats = {}
            for estado_code, estado_name in Transaccion.ESTADOS_PEDIDO:
                count = transacciones.filter(estado_pedido=estado_code).count()
                stats[estado_name] = count
                
            self.stdout.write('\n📊 Estadísticas de estados:')
            for estado, count in stats.items():
                self.stdout.write(f'   • {estado}: {count}')
                
        else:
            # Solo mostrar estadísticas actuales
            self.stdout.write('📋 Estados actuales de pedidos:')
            for estado_code, estado_name in Transaccion.ESTADOS_PEDIDO:
                count = transacciones.filter(estado_pedido=estado_code).count()
                if count > 0:
                    self.stdout.write(f'   • {estado_name}: {count}')
            
            self.stdout.write(f'\n💡 Total de transacciones autorizadas: {transacciones.count()}')
            self.stdout.write('💡 Usa --diversificar para crear datos de demo')
            self.stdout.write('💡 Usa --reset para reiniciar todos los estados')
