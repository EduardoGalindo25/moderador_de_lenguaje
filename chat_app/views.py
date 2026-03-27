import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

# Initialize the OpenAI client pointing to DeepSeek API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", ""), 
    base_url="https://api.deepseek.com/beta" if "beta" in os.getenv("DEEPSEEK_API_KEY", "") else "https://api.deepseek.com"
)

def chat_index(request):
    # Initialize the session if not present
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    
    return render(request, 'chat_app/chat.html', {
        'message_count': len([m for m in request.session.get('chat_history', []) if m['role'] == 'user'])
    })

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
                
            history = request.session.get('chat_history', [])
            
            # Count user messages so far
            user_msg_count = len([m for m in history if m['role'] == 'user'])
            
            if user_msg_count >= 10:
                return JsonResponse({'error': 'Chat session is over.', 'over': True}, status=400)
                
            # Add new user message to history
            history.append({'role': 'user', 'content': user_message})
            user_msg_count += 1
            request.session['chat_history'] = history
            
            # Prepare API call to DeepSeek
            if user_msg_count < 10:
                system_prompt = {
                    "role": "system",
                    "content": (
                        "Eres un conversador casual y amigable. "
                        "El usuario interactuará contigo. Tienes dos reglas ESTRICTAS:\n"
                        "1. Si el usuario usa lenguaje ofensivo, insultos o toxicidad manifiesta, "
                        "DEBES DEJAR DE ACTUAR de forma casual y RESPONDER con palabras de advertencia sobre mal uso del lenguaje."
                        "2. Si el comentario del usuario es muy positivo y amable, debes incluir naturalmente "
                        "un agradecimiento en tu respuesta, por ejemplo: '¡Gracias por tus buenas palabras!'.\n"
                        "Sé conciso y natural en tus respuestas."
                    )
                }
                
                messages_for_api = [system_prompt] + history
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_for_api,
                )
                
                bot_reply = response.choices[0].message.content
                history.append({'role': 'assistant', 'content': bot_reply})
                request.session['chat_history'] = history
                
                return JsonResponse({
                    'reply': bot_reply,
                    'message_count': user_msg_count,
                    'is_final': False
                })
                
            else:
                # 10th message logic
                system_prompt = {
                    "role": "system",
                    "content": """
Eres un Moderador de Comentarios Inteligente y Evaluador Lingüístico.
El usuario ha enviado el último mensaje de la conversación.
Analiza la conversación acumulada: redacción, estadísticas de vocabulario, comportamiento y toxicidad (Escala: 100=Perfecto/Respetuoso, 0=Tóxico/Ofensivo).

REGLA IMPORTANTE: Para que una palabra (ya sea positiva o negativa) sea considerada como recurrente o incluida en "palabras_mas_usadas", el usuario debe haberla repetido AL MENOS 3 VECES a lo largo de la conversación. Si una palabra se usó solo 1 o 2 veces, NO debe ser listada como palabra frecuente o muy usada.

DEVUELVE ESTRICTAMENTE UN JSON VÁLIDO Y NADA MÁS. SIN EXPLICACIONES, SIN MARKDOWN DE BLOQUE DE CÓDIGO (NO USES ```json O ```). 
LA RESPUESTA DEBE SER PARSEABLE POR JSON.LOADS() DIRECTAMENTE.
ESTRUCTURA EXACTA REQUERIDA:
{
  "evaluacion_redaccion": {
    "calificacion": 85,
    "comentario": "comentario general",
    "sugerencias": "sugerencias",
    "desglose": {
      "ortografia": "Buena",
      "gramatica": "Aceptable",
      "claridad": "Alta",
      "coherencia": "Alta",
      "formalidad": "Casual"
    }
  },
  "estadisticas_vocabulario": {
    "palabras_mas_usadas": ["hola", "sistema"],
    "porcentaje_positivos": 60,
    "porcentaje_negativos": 10,
    "porcentaje_neutrales": 30
  },
  "calificacion_usuario": {
    "puntaje": 90,
    "clasificacion": "Respetuoso"
  }
}
"""
                }
                
                # Convertir historial a texto plano para evitar que el modelo
                # continúe el patron de "moderador casual" en lugar de generar JSON
                transcript = "\n".join([
                    f"[{'USUARIO' if m['role'] == 'user' else 'BOT'}]: {m['content']}"
                    for m in history
                ])

                messages_for_api = [
                    system_prompt,
                    {"role": "user", "content": f"Aquí está la conversación completa a evaluar:\n\n{transcript}"}
                ]
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_for_api
                )
                
                bot_reply = response.choices[0].message.content.strip()
                
                # Try to clean up markdown if the API ignores the strict prompt
                if bot_reply.startswith("```json"):
                    bot_reply = bot_reply[7:]
                if bot_reply.endswith("```"):
                    bot_reply = bot_reply[:-3]
                bot_reply = bot_reply.strip()
                
                try:
                    bot_reply_json = json.loads(bot_reply)
                except json.JSONDecodeError:
                    bot_reply_json = {"error": "DeepSeek response was not valid JSON", "raw": bot_reply}
                    
                # Optionally clear session after finishing
                request.session['chat_history'] = []
                
                return JsonResponse({
                    'reply': bot_reply_json,
                    'message_count': user_msg_count,
                    'is_final': True
                })
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)
