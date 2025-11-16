import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def enviar_correo(destinatario, asunto, html_contenido):
    """
    Envía un correo electrónico usando Gmail SMTP
    """
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    if not email_user or not email_password:
        logger.error("Credenciales de correo no configuradas en variables de entorno")
        return False
    
    try:
        # Crear mensaje
        mensaje = MIMEMultipart('alternative')
        mensaje['From'] = f"Tindo Store <{email_user}>"
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        
        # Adjuntar contenido HTML
        parte_html = MIMEText(html_contenido, 'html', 'utf-8')
        mensaje.attach(parte_html)
        
        # Conectar a Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()
            servidor.login(email_user, email_password)
            servidor.send_message(mensaje)
        
        logger.info(f"✓ Correo enviado exitosamente a {destinatario}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error enviando correo a {destinatario}: {str(e)}")
        return False


def generar_html_nueva_orden(orden_data):
    """
    Genera HTML para notificación al admin de nueva orden
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px;
                color: #333;
            }}
            .alert-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 4px;
            }}
            .order-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .detail-row {{
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: 600;
                color: #555;
            }}
            .value {{
                color: #333;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Nueva Orden Recibida</h1>
            </div>
            <div class="content">
                <div class="alert-box">
                    <strong>¡Atención!</strong> Se ha recibido una nueva orden en Tindo Store.
                </div>
                
                <h2 style="color: #333; margin-top: 25px;">Detalles de la Orden</h2>
                <div class="order-details">
                    <div class="detail-row">
                        <span class="label">Orden #:</span>
                        <span class="value">{orden_data['orden_id']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Fecha:</span>
                        <span class="value">{orden_data['fecha']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Cliente:</span>
                        <span class="value">{orden_data['nombre']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Correo:</span>
                        <span class="value">{orden_data['correo']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Producto:</span>
                        <span class="value">{orden_data['producto']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Paquete:</span>
                        <span class="value">{orden_data['paquete']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Cantidad:</span>
                        <span class="value">{orden_data.get('cantidad', 1)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Precio unitario:</span>
                        <span class="value">${orden_data.get('precio_unitario', orden_data.get('precio', '0.00'))}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Total:</span>
                        <span class="value"><strong>${orden_data.get('total', orden_data.get('precio', '0.00'))}</strong></span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Player ID:</span>
                        <span class="value">{orden_data['player_id']}</span>
                    </div>
                    {f'''<div class="detail-row">
                        <span class="label">Zone ID:</span>
                        <span class="value">{orden_data['zone_id']}</span>
                    </div>''' if orden_data.get('zone_id') else ''}
                    <div class="detail-row">
                        <span class="label">Método de pago:</span>
                        <span class="value">{orden_data['metodo_pago']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Referencia:</span>
                        <span class="value"><strong>{orden_data['referencia']}</strong></span>
                    </div>
                </div>
                
                <p style="margin-top: 20px; color: #666;">
                    Por favor, procesa esta orden lo antes posible.
                </p>
            </div>
            <div class="footer">
                <p>Tindo Store - Sistema de Notificaciones Automáticas</p>
                <p style="font-size: 12px; color: #999;">Este es un correo automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """


def generar_html_orden_creada(orden_data):
    """
    Genera HTML para notificación al cliente cuando se crea la orden
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px;
                color: #333;
                line-height: 1.6;
            }}
            .success-box {{
                background-color: #d1ecf1;
                border-left: 4px solid #17a2b8;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 4px;
            }}
            .order-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .detail-row {{
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: 600;
                color: #555;
            }}
            .value {{
                color: #333;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .highlight {{
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                border-left: 4px solid #ffc107;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Orden Recibida</h1>
            </div>
            <div class="content">
                <p style="font-size: 18px; color: #333;"><strong>Hola {orden_data['nombre']},</strong></p>
                
                <div class="success-box">
                    <strong>¡Gracias por tu compra!</strong> Nos complace informarte que tu pedido ha sido recibido exitosamente.
                </div>
                
                <p>Tu orden está siendo procesada y será completada en breve. A continuación los detalles:</p>
                
                <h2 style="color: #333; margin-top: 25px;">Detalles de la Orden</h2>
                <div class="order-details">
                    <div class="detail-row">
                        <span class="label">Orden #:</span>
                        <span class="value">{orden_data['orden_id']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Fecha:</span>
                        <span class="value">{orden_data['fecha']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Producto:</span>
                        <span class="value">{orden_data['producto']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">ID de jugador:</span>
                        <span class="value">{orden_data['player_id']}</span>
                    </div>
                    {f'''<div class="detail-row">
                        <span class="label">Zone ID:</span>
                        <span class="value">{orden_data['zone_id']}</span>
                    </div>''' if orden_data.get('zone_id') else ''}
                    <div class="detail-row">
                        <span class="label">Paquete adquirido:</span>
                        <span class="value">{orden_data['paquete']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Cantidad:</span>
                        <span class="value">{orden_data.get('cantidad', 1)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Precio unitario:</span>
                        <span class="value">USD ${orden_data.get('precio_unitario', orden_data.get('precio', '0.00'))}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Total pagado:</span>
                        <span class="value"><strong>USD ${orden_data.get('total', orden_data.get('precio', '0.00'))}</strong></span>
                    </div>
                </div>
                
                <div class="highlight">
                    <strong>📋 Estado:</strong> Tu orden está pendiente de procesamiento. Te notificaremos cuando sea completada.
                </div>
                
                <p style="margin-top: 20px;">
                    Si necesitas asistencia o tienes alguna consulta, nuestro equipo de soporte está disponible para ayudarte en todo momento.
                </p>
                
                <p style="margin-top: 30px; color: #666;">
                    Atentamente,<br>
                    <strong>Equipo de Tindo Store</strong>
                </p>
            </div>
            <div class="footer">
                <p>Tindo Store - Tu tienda de confianza para recargas de juegos</p>
                <p style="font-size: 12px; color: #999; margin-top: 10px;">
                    Si no realizaste esta compra, por favor contáctanos de inmediato.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def generar_html_orden_completada(orden_data):
    """
    Genera HTML para notificación al cliente cuando se completa la orden
    """
    es_giftcard = orden_data.get('producto_tipo') == 'giftcard'
    codigo_giftcard = orden_data.get('codigo_giftcard', '')
    
    # Sección del código de gift card si aplica
    codigo_section = ''
    if es_giftcard and codigo_giftcard:
        codigo_section = f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; 
                    border-radius: 10px; 
                    margin: 25px 0; 
                    text-align: center;">
            <h3 style="color: white; margin: 0 0 15px 0; font-size: 18px;">
                🎁 Tu Código de Gift Card
            </h3>
            <div style="background-color: white; 
                        padding: 15px 20px; 
                        border-radius: 8px; 
                        display: inline-block;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <code style="font-size: 24px; 
                            font-weight: bold; 
                            color: #333; 
                            letter-spacing: 2px;
                            font-family: 'Courier New', monospace;">
                    {codigo_giftcard}
                </code>
            </div>
            <p style="color: white; margin: 15px 0 0 0; font-size: 14px;">
                Copia este código para canjearlo en la plataforma
            </p>
        </div>
        '''
    
    titulo = "🎁 ¡Tu Gift Card está Lista!" if es_giftcard else "🎉 ¡Recarga Completada!"
    mensaje_exito = "¡Tu gift card ha sido procesada exitosamente!" if es_giftcard else "¡Tu recarga ha sido procesada exitosamente!"
    mensaje_sub = "Ya puedes canjear tu código" if es_giftcard else "Ya puedes disfrutar de tu compra"
    mensaje_principal = "Nos complace informarte que tu pedido ha sido completado con éxito. " + ("A continuación encontrarás tu código para canjear." if es_giftcard else "Los recursos han sido agregados a tu cuenta.")
    
    # Nota final según el tipo
    nota_final = '''
        <div class="note">
            <strong>💡 Instrucciones de canje:</strong> Ingresa este código en la plataforma correspondiente para activar tu gift card. Si tienes problemas para canjear, contáctanos.
        </div>
    ''' if es_giftcard else '''
        <div class="note">
            <strong>💡 Nota importante:</strong> Si no ves los recursos en tu cuenta, por favor verifica que hayas ingresado el ID correcto y espera unos minutos. Si el problema persiste, contáctanos.
        </div>
    '''
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px;
                color: #333;
                line-height: 1.6;
            }}
            .success-box {{
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 4px;
                text-align: center;
            }}
            .success-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .order-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .detail-row {{
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: 600;
                color: #555;
            }}
            .value {{
                color: #333;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .note {{
                background-color: #e7f3ff;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                border-left: 4px solid #0066cc;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{titulo}</h1>
            </div>
            <div class="content">
                <p style="font-size: 18px; color: #333;"><strong>Hola {orden_data['nombre']},</strong></p>
                
                <div class="success-box">
                    <div class="success-icon">✅</div>
                    <h2 style="margin: 10px 0; color: #28a745;">{mensaje_exito}</h2>
                    <p style="margin: 0; color: #666;">{mensaje_sub}</p>
                </div>
                
                <p>{mensaje_principal}</p>
                
                {codigo_section}
                
                <h2 style="color: #333; margin-top: 25px;">Detalles de la Orden</h2>
                <div class="order-details">
                    <div class="detail-row">
                        <span class="label">Orden #:</span>
                        <span class="value">{orden_data['orden_id']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Fecha de compra:</span>
                        <span class="value">{orden_data['fecha']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Producto:</span>
                        <span class="value">{orden_data['producto']}</span>
                    </div>
                    {f'''<div class="detail-row">
                        <span class="label">ID de jugador:</span>
                        <span class="value">{orden_data['player_id']}</span>
                    </div>''' if orden_data.get('player_id') else ''}
                    {f'''<div class="detail-row">
                        <span class="label">Zone ID:</span>
                        <span class="value">{orden_data['zone_id']}</span>
                    </div>''' if orden_data.get('zone_id') else ''}
                    <div class="detail-row">
                        <span class="label">Paquete adquirido:</span>
                        <span class="value">{orden_data['paquete']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Costo:</span>
                        <span class="value"><strong>USD ${orden_data['precio']}</strong></span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Estado:</span>
                        <span class="value" style="color: #28a745; font-weight: bold;">✅ COMPLETADA</span>
                    </div>
                </div>
                
                {nota_final}
                
                <p style="margin-top: 20px;">
                    ¡Gracias por confiar en Tindo Store! Esperamos verte pronto para tu próxima {'gift card' if es_giftcard else 'recarga'}.
                </p>
                
                <p style="margin-top: 30px; color: #666;">
                    Si necesitas asistencia o tienes alguna consulta, nuestro equipo de soporte está disponible para ayudarte en todo momento.
                </p>
                
                <p style="margin-top: 30px; color: #666;">
                    Atentamente,<br>
                    <strong>Equipo de Tindo Store</strong>
                </p>
            </div>
            <div class="footer">
                <p>Tindo Store - Tu tienda de confianza para recargas de juegos y gift cards</p>
                <p style="font-size: 12px; color: #999; margin-top: 10px;">
                    ¿Te gustó nuestro servicio? ¡Recomiéndanos con tus amigos!
                </p>
            </div>
        </div>
    </body>
    </html>
    """
