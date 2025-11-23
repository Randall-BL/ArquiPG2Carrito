"""
Script de prueba para verificar la configuración de Twilio
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notifications import TwilioNotifier
import config


def main():
    print("=" * 60)
    print("PRUEBA DE CONFIGURACIÓN TWILIO")
    print("=" * 60)
    
    # Verificar configuración
    print("\n📋 Verificando configuración...")
    print(f"   Account SID: {config.TWILIO_ACCOUNT_SID[:10]}...")
    print(f"   Auth Token: {config.TWILIO_AUTH_TOKEN[:10]}...")
    print(f"   Número origen: {config.TWILIO_PHONE_FROM}")
    print(f"   Número destino: {config.TWILIO_PHONE_TO}")
    
    # Verificar si está configurado
    if config.TWILIO_ACCOUNT_SID == "tu_account_sid_aqui":
        print("\n❌ ERROR: Credenciales no configuradas")
        print("\nPor favor edita config.py y agrega:")
        print("1. Tu Account SID de Twilio")
        print("2. Tu Auth Token de Twilio")
        print("3. Tu número Twilio (FROM)")
        print("\nConsulta CONFIGURAR_TWILIO.md para instrucciones")
        return
    
    # Crear notificador
    print("\n🔧 Inicializando cliente Twilio...")
    notifier = TwilioNotifier()
    
    if not notifier.is_configured():
        print("❌ El cliente Twilio no pudo inicializarse")
        print("Verifica tu configuración y que Twilio esté instalado")
        return
    
    # Probar conexión
    print("\n🔌 Probando conexión con Twilio...")
    if not notifier.test_connection():
        print("❌ Error al conectar con Twilio")
        print("Verifica tus credenciales")
        return
    
    # Preguntar si enviar SMS de prueba
    print("\n" + "=" * 60)
    print("¿Deseas enviar un SMS de prueba?")
    print(f"Se enviará a: {config.TWILIO_PHONE_TO}")
    print("=" * 60)
    
    respuesta = input("\n¿Enviar SMS de prueba? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n📤 Enviando SMS de prueba...")
        
        mensaje = (
            "🧪 Prueba del Sistema de Notificaciones\n\n"
            "Este es un mensaje de prueba del carrito ESP32.\n"
            "Si recibes este mensaje, el sistema está funcionando correctamente."
        )
        
        success = notifier.send_custom_message(mensaje)
        
        if success:
            print("\n✅ ¡SMS ENVIADO EXITOSAMENTE!")
            print(f"   Revisa el teléfono {config.TWILIO_PHONE_TO}")
            print("\n📊 Puedes ver el estado en:")
            print("   https://console.twilio.com/us1/monitor/logs/sms")
        else:
            print("\n❌ Error al enviar SMS")
            print("   Posibles causas:")
            print("   1. Número no verificado (si usas cuenta Trial)")
            print("   2. Credenciales incorrectas")
            print("   3. Saldo insuficiente")
            print("   4. Formato de número incorrecto")
    else:
        print("\n⏭️  SMS de prueba omitido")
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print("✅ Twilio configurado correctamente")
    print("✅ Conexión exitosa")
    print("✅ Sistema listo para detectar colisiones")
    print("\nCuando el ESP32 envíe 'Colisión detectada',")
    print(f"se enviará automáticamente un SMS a {config.TWILIO_PHONE_TO}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
